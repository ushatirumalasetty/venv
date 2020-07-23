
import json
import os

from django_swagger_utils.core.parsers.swagger_parser import SwaggerParser
from django_swagger_utils.core.utils.check_path_exists import check_path_exists
from django_swagger_utils.drf_server.utils.server_gen.get_api_environment import check_to_execute_mock_test_for_operation
from io import open


def get_app_test_labels(base_dir, app_name):
    '''

    :param base_dir: your project directory
    :param app_name: app name
    :return: returns list of views for which mocktests are to be done
    '''
    app_dir=os.path.join(base_dir,app_name)
    views_dir = os.path.join(app_dir,"views")
    spec_file_path = os.path.join(os.path.join(app_dir, "api_specs"),"api_spec.json")
    if not spec_file_path:
        raise Exception(" %s/api_specs/api_spec.json missing" % app_name)
    with open(spec_file_path) as f:
        spec_file_contents = f.read()
        try:
            spec_json = json.loads(spec_file_contents)
        except ValueError:
            print("The \"%s/api_specs/api_spec.json\" is not a proper JSON." % app_name)
            exit(1)

    parser = SwaggerParser(spec_json=spec_json)
    # TODO code duplicacy apidoc and here
    op_of_last_version = []

    with open(base_dir + "/" + app_name + "/api_specs/api_spec.json") as src_json:
        src = json.load(src_json)

    operation_id_wise_group_name = {}
    for path_name, path in list(parser.paths().items()):

        for method, method_props in list(path.items()):
            # Handle common parameters later

            if (method == 'get') or (method == 'post') or (method == 'delete') or (method == 'put'):
                operation_id = method_props.get("operationId")
                op_of_last_version.append(operation_id)

                if method_props.get('x-group'):
                    operation_id_wise_group_name[operation_id] = \
                        method_props.get('x-group')

    group_names = list(operation_id_wise_group_name.values())
    #make a list of views to be subjected to mocktest
    req_endpoints = []
    for dir_name in os.listdir(views_dir):

        if dir_name in group_names:
            endpoint_dir_path = views_dir + "/" + dir_name
            endpoint_names = os.listdir(endpoint_dir_path)
            group_name = dir_name
        else:
            endpoint_names = [dir_name]
            group_name = ''
            endpoint_dir_path = views_dir

        for endpoint_name in endpoint_names:
            if os.path.isdir(os.path.join(endpoint_dir_path, endpoint_name)):
                #the below function call will return a bool,if its true add it to list
                execute_mock_test = check_to_execute_mock_test_for_operation(
                    app_name, endpoint_name, group_name)
                if execute_mock_test:
                    req_endpoints.append(endpoint_name)

    dir_list = []
    #adding tests path to the list
    for endpoint_name in req_endpoints:
        if endpoint_name in op_of_last_version:
            #the reason this is not written using os.apth.join() is django import statements support
            #dots to join files not '/'

            group_name = operation_id_wise_group_name.get(endpoint_name)
            if group_name:
                tests_path_for_import = \
                    app_name + ".views." + group_name + "." + \
                    endpoint_name + ".tests"
                endpoint_dir_path = views_dir + "/" + group_name
            else:
                tests_path_for_import = app_name + ".views." + endpoint_name + ".tests"
                endpoint_dir_path = views_dir

            test_case_init_path=os.path.join(os.path.join(os.path.join(
                endpoint_dir_path, endpoint_name ), "tests"), "__init__.py")

            test_path = check_path_exists(test_case_init_path)
            if test_path:
                dir_list.append(tests_path_for_import)
    #if nothing is added that means all tests are marked to false , terminate the programs giving a message
    if len(dir_list) == 0:
        print("all mock tests marked false,no tests to run ")
        print("please change execute mock test to true wherever required")
        exit(1)

    return dir_list
