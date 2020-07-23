
import datetime
import importlib
import json
import logging
import uuid
import os

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand, CommandError
from django.test.runner import DiscoverRunner

logger = logging.getLogger('dsu.debug')


class GetTestNames(DiscoverRunner):
    def __init__(self, **kwargs):
        super(GetTestNames, self).__init__(**kwargs)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        suite = self.build_suite(test_labels, extra_tests)
        test_names = []
        for each_test in suite._tests:
            cls = each_test.__class__
            test_name = "%s.%s" % (cls.__module__, cls.__name__)
            test_names.append(test_name)
        return test_names


class TestsWorkflow(object):
    run_id = None
    workflow_id = None
    waiting_count = 0

    def __init__(self, test_cases, lambda_function_name, domain, worker_name, worker_version, worker_tasks_list,
                 lambda_role_name, api_gateway_name, api_stage, region_name='eu-west-1'):

        self.test_cases = test_cases
        self.lambda_function_name = lambda_function_name
        self.domain = domain
        self.worker_name = worker_name
        self.worker_version = worker_version
        self.worker_tasks_list = worker_tasks_list
        self.lambda_role_name = lambda_role_name
        self.api_gateway_name = api_gateway_name
        self.api_stage = api_stage

        self.lambda_client = boto3.client('lambda', region_name=region_name)
        self.swf_client = boto3.client('swf', region_name=region_name)
        self.iam_client = boto3.client('iam', region_name=region_name)
        self.api_gateway_client = boto3.client('apigateway', region_name=region_name)

    def run_tests(self):
        self.start_workflow()
        while not self.count_closed_workflow():
            pass
        return self.get_events()

    def start_workflow(self):

        self.workflow_id = str(uuid.uuid4())

        response = self.swf_client.start_workflow_execution(
            domain=self.domain,
            workflowId=self.workflow_id,
            workflowType={
                "name": self.worker_name,
                "version": self.worker_version
            },
            taskList={
                'name': self.worker_tasks_list
            },
            taskStartToCloseTimeout='60',
            executionStartToCloseTimeout='3600',
            childPolicy='TERMINATE',
            lambdaRole=self.get_iam_role_arn(),
            input=self.generate_jackson_json_input(),
        )
        self.run_id = response["runId"]
        print("Workflow Started: [Run Id: %s]" % self.run_id)

    def generate_jackson_json_input(self):
        stage_vars_list = []
        for key, val in list(self.get_stage_vars().items()):
            inner_str = "[\"com.ibtspl.devops.django.Stage_vars\",{\"key_name\": \"%s\",\"value\": \"%s\"}]" % (
                key, val)
            stage_vars_list.append(inner_str)
        stage_vars_str = ",".join(stage_vars_list)
        json_str = "[\"[Ljava.lang.Object;\",[[\"com.ibtspl.devops.django.LambdaInput\",{\"stage_vars\": [\"[Lcom.ibtspl.devops.django.Stage_vars;\",[ %s ]],\"function_name\": \"%s\",\"test_cases\": %s }]]]" % (
            stage_vars_str, self.get_lambda_function_arn(), json.dumps(self.test_cases))
        return json_str

    def get_lambda_function_arn(self):
        try:
            response = self.lambda_client.get_function(
                FunctionName=self.lambda_function_name,

            )
            arn = response["Configuration"]["FunctionArn"]
            account_id = arn.split(":")[4]
            return "%s:%s" % (account_id, self.lambda_function_name)
        except ClientError as err:
            logger.error(err)
            raise Exception("Lambda Function Not Found")

    def get_iam_role_arn(self):
        response = self.iam_client.get_role(
            RoleName=self.lambda_role_name
        )
        return response["Role"]["Arn"]

    def count_closed_workflow(self):

        self.waiting_count += 1
        # print "Waiting for Workflow to Complete Execution ..... #%d" % self.waiting_count
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        response = self.swf_client.count_closed_workflow_executions(
            domain=self.domain,
            startTimeFilter={
                'oldestDate': yesterday,
                'latestDate': today
            },
            executionFilter={
                'workflowId': self.workflow_id
            },
        )
        return response["count"]

    def get_events(self):

        request_dict = {
            'domain': self.domain,
            'execution': {
                'workflowId': self.workflow_id,
                'runId': self.run_id
            }
        }
        events = []
        next_page_token = None

        while (1):
            if next_page_token:
                request_dict["nextPageToken"] = next_page_token

            response = self.swf_client.get_workflow_execution_history(**request_dict)
            next_page_token = response.get("nextPageToken", None)
            events.extend(response['events'])

            if not next_page_token:
                break

        return events

    def get_stage_vars(self):

        apis = [api for api in self.api_gateway_client.get_rest_apis(limit=500)['items'] if api['name'] == self.api_gateway_name]
        if not apis:
            print('Cannot find any api with name %s' % self.api_gateway_name)
            raise
        if len(apis) > 1:
            print('Found multiple apis with name %s. Choosing the first one to import stage_vars' % self.api_gateway_name)
        api_id = apis[0]['id']
        if not api_id:
            print('Cannot find any api with name %s' % self.api_gateway_name)
            raise

        stage_vars = self.api_gateway_client.get_stage(restApiId=api_id, stageName=self.api_stage)['variables']

        # updating the db stage vars to run tests in non postgres sql environment
        stage_vars['RDS_DB_ENGINE'] = 'django.db.backends.sqlite3'
        stage_vars['RDS_DB_NAME'] = '/tmp/%s.sqlite3' % str(uuid.uuid4())
        stage_vars['RDS_USERNAME'] = ""
        stage_vars['RDS_PASSWORD'] = ""
        stage_vars['RDS_HOSTNAME'] = ""
        stage_vars['RDS_PORT'] = ""
        return stage_vars


def print_run_tests_report(events_list):
    total_tests = 0
    success_tests = 0
    print("Running Tests")
    print("========================================")

    for events in events_list:
        for event in events:
            # print event, "\n\n\n"
            if event["eventType"] == "LambdaFunctionFailed":
                lambda_function_attrs = event["lambdaFunctionFailedEventAttributes"]
                scheduled_event_id = lambda_function_attrs["scheduledEventId"]
                details = lambda_function_attrs["details"]

                scheduled_event = get_event_by_id(scheduled_event_id, events)
                if not details.find("Service: AWSLambda; Status Code: 429;") and \
                    not details.find("Service: AWSLambda; Status Code: 500;"):
                    total_tests += 1
                    print_event_input(total_tests, scheduled_event)
                    print("Status: Failed")
                    print("Stack Traces:")
                    print(details)
                    print("========================================")

            if event["eventType"] == "LambdaFunctionCompleted":
                lambda_function_attrs = event["lambdaFunctionCompletedEventAttributes"]
                scheduled_event_id = lambda_function_attrs["scheduledEventId"]
                result = lambda_function_attrs["result"]
                scheduled_event = get_event_by_id(scheduled_event_id, events)
                total_tests += 1
                success_tests += 1
                print_event_input(total_tests, scheduled_event)
                print("Status: Success")
                # print "Stack Traces:"
                # print result
                print("========================================")

    failed_tests = total_tests - success_tests
    print("Total Tests: %d " % total_tests)
    print("Success: %d" % success_tests)
    print("Failure: %d" % failed_tests)

    if failed_tests:
        exit(1)
    exit(0)


def print_event_input(test_no, event):
    lambda_function_attrs = event["lambdaFunctionScheduledEventAttributes"]
    event_input = lambda_function_attrs["input"]
    event_input = json.loads(event_input)
    print("Test #%d, %s" % (test_no, event_input["Key"]))


def get_event_by_id(id, events):
    for each_event in events:
        if each_event['eventId'] == id:
            return each_event


def get_test_case(event):
    lambda_function_attrs = event["lambdaFunctionScheduledEventAttributes"]
    event_input = lambda_function_attrs["input"]
    event_input = json.loads(event_input)
    return event_input["Key"]


def get_retry_test_cases(events):
    test_cases = []
    for event in events:
        if event["eventType"] == "LambdaFunctionFailed":
            lambda_function_attrs = event["lambdaFunctionFailedEventAttributes"]
            scheduled_event_id = lambda_function_attrs["scheduledEventId"]
            details = lambda_function_attrs["details"]
            scheduled_event = get_event_by_id(scheduled_event_id, events)
            test_case = get_test_case(scheduled_event)
            if details.find("Service: AWSLambda; Status Code: 429;") or \
                details.find("Service: AWSLambda; Status Code: 500;"):
                test_cases.append(test_case)
                # print "-------------------"
                # print "Status: Retry [%s]" % test_case
                # print "Stack Traces:"
                # print details
                # print "-------------------\n"

    return test_cases


class Command(BaseCommand):
    can_import_settings = True
    help = 'Run Tests for basic of swagger util apps'

    def add_arguments(self, parser):
        parser.add_argument('stage', help='Branch / API Stage Name', default='alpha')
        parser.add_argument('app', nargs='*', type=str, help="list of apps")

    def handle(self, *args, **options):
        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        try:
            apps = options['app']
            if not apps:
                apps = swagger_apps

            stage = options["stage"]
            swf_workflow_version = "8"

            try:
                zappa_settings = getattr(importlib.import_module('zappa_deploy'), 'ZAPPA_SETTINGS')
            except ImportError as err:
                self.stderr.write(err)
                raise CommandError('Use this command with zappa settings only')

            function_name = zappa_settings[stage]["lambda_function"]
            lambda_function_name = function_name + "_test"

            workflow_domain = "DjangoTesting"
            workflow_worker_name = "DjangoTestingWorker.startIndividualTests"
            workflow_worker_version = "%s.0" % swf_workflow_version
            workflow_worker_tasks_list = "DjangoTestingWorkflowTaskList%s" % swf_workflow_version
            workflow_lambda_role = "swf_lambda"

            test_labels = []
            base_dir = settings.BASE_DIR
            for app_name in apps:
                from django_swagger_utils.drf_server.utils.server_gen.get_app_test_labels import get_app_test_labels
                app_test_labels = get_app_test_labels(base_dir=base_dir,app_name=app_name)
                test_labels.extend(app_test_labels)
            # print test_labels
            tests = GetTestNames()
            test_cases = tests.run_tests(test_labels=test_labels)
            # print test_cases

            # for i in range(1, 6):
            #     test_cases.extend(test_cases)
            # step = 200
            # for i in range(0, len(test_cases), step):
            #     print "Batch %d" % ((i / step) + 1)
            #     test_work_flow = TestsWorkflow(test_cases[i:i + step], lambda_function_name, workflow_domain,
            #                                    workflow_worker_name, workflow_worker_version,
            #                                    workflow_worker_tasks_list, workflow_lambda_role,
            #                                    api_gateway_name=function_name, api_stage=stage)
            #     events = test_work_flow.run_tests()
            #     events_list.append(events)
            # print_run_tests_report(events_list)
            count = 1
            events_list = []
            region_name = os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-1")
            while len(test_cases):
                print("=========================================================")
                print("Execution No : ", count)
                print("Test Cases : ", len(test_cases))
                test_work_flow = TestsWorkflow(test_cases, lambda_function_name, workflow_domain,
                                               workflow_worker_name, workflow_worker_version,
                                               workflow_worker_tasks_list, workflow_lambda_role,
                                               api_gateway_name=function_name, api_stage=stage,
                                               region_name=region_name)
                events = test_work_flow.run_tests()
                print("=========================================================")
                print("Retry Test Cases")
                test_cases = get_retry_test_cases(events)
                print("=========================================================\n\n\n")
                events_list.append(events)
                count += 1
            print_run_tests_report(events_list)
        except Exception as err:
            self.stderr.write(str(err))
            print(err)
            exit(1)
            raise
