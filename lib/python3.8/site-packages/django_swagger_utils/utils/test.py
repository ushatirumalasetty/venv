

import base64
import importlib
import json
import logging

from django.conf import settings
from future import standard_library
from snapshottest.django import TestRunner
from snapshottest.unittest import TestCase as uTestCase

from django_swagger_utils.drf_server.utils.server_gen.custom_test_utils import \
    CustomTestUtils

standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error

DATABASE_ENGINE = settings.DATABASES.get('default', {}).get('ENGINE')

if DATABASE_ENGINE != 'django.db.backends.sqlite3':
    from rest_framework.test import APITransactionTestCase as rAPITestCase
else:
    from rest_framework.test import APITestCase as rAPITestCase

logger = logging.getLogger('dsu.debug')


class APITestCase(uTestCase, rAPITestCase):
    pass


class CustomAPITestCase(APITestCase, CustomTestUtils):
    app_name = None
    operation_name = None
    request_method = None
    url_suffix = None
    test_case_dict = None
    if DATABASE_ENGINE != 'django.db.backends.sqlite3':
        reset_sequences = True

    def __init__(self, *args, **kwargs):
        super(CustomAPITestCase, self).__init__(*args, **kwargs)
        self.maxDiff = None
        self.url = kwargs.get("url")
        self.foo_user = None

    def setupUser(self, username, password):
        self.foo_user = self._create_user(username, password)

    def setupOAuth(self, scopes):
        self.app_foo = self._create_application('app foo_user 1',
                                                self.foo_user)
        self.foo_access_token = self._get_access_token(user=self.foo_user,
                                                       app=self.app_foo,
                                                       scope=scopes)
        self.mock_auth(self.client, self.foo_access_token.token)

    def default_test_case(self):
        test_case_request_dict = self.test_case_dict["request"]

        header_parameters = test_case_request_dict.get("header_params", {})
        path_parameters = test_case_request_dict.get("path_params", {})
        if self.url:
            url = self.url.format(**path_parameters)
        else:
            url_suffix = self.url_suffix.format(**path_parameters)
            url = '/api/%s/%s' % (self.app_name, url_suffix)

        query_parameters = test_case_request_dict.get("query_params", {})
        request_method_function = getattr(self.client, self.request_method)

        securities = test_case_request_dict["securities"]
        oauth_scopes = []
        username = None
        password = None
        for security, security_def in list(securities.items()):
            if security_def["type"] == "oauth2":
                oauth_scopes.extend(security_def["scopes"])
            elif security_def["type"] == "apiKey":
                if security_def["in"] == "header":
                    header_parameters.update(
                        {security_def["header_name"]: security_def["value"]})

                    from django.conf import settings
                    create_user_on_api_key_header = getattr(
                        settings, 'CREATE_USER_ON_API_KEY_HEADER', None)
                    if create_user_on_api_key_header:
                        username = security_def.get("username", "username")
                        password = security_def.get("password", "password")
                else:
                    query_parameters.update(
                        {security_def["name"]: security_def["value"]})
            elif security_def["type"] == "basic":
                auth_value = 'Basic ' + base64.b64encode('%s:%s' % (
                    security_def["username"], security_def["password"]))
                header_parameters.update({"HTTP_AUTHORIZATION": auth_value})
                username = security_def["username"]
                password = security_def["password"]
        if oauth_scopes:
            oauth_scopes = " ".join(oauth_scopes)
            username = "username"
            password = "password"
        if username:
            self.setupUser(username=username, password=password)
        if oauth_scopes:
            self.setupOAuth(oauth_scopes)

        # update headers based on self.foo_user
        if self.foo_user:
            from django.conf import settings
            foo_user_to_headers_converter = getattr(
                settings, 'FOO_USER_TO_HEADERS_CONVERTER', None)
            if foo_user_to_headers_converter:
                foo_user_converter = getattr(importlib.import_module(
                    ".".join(foo_user_to_headers_converter.split(".")[:-1])),
                    foo_user_to_headers_converter.split(".")[-1]
                )
                headers_to_update = foo_user_converter(self.foo_user)
                if headers_to_update:
                    header_parameters.update(headers_to_update)

        test_case_request_dict = self.test_case_dict["request"]
        data = test_case_request_dict["body"]

        if query_parameters:
            url += "?" + urllib.parse.urlencode(query_parameters, doseq=True)
        if self.request_method == "get":
            wrapped_request_data = query_parameters
        else:
            from django.conf import settings
            django_swagger_utils_settings = settings.SWAGGER_UTILS
            defaults = django_swagger_utils_settings["DEFAULTS"]
            if defaults.get("REQUEST_WRAPPING_REQUIRED", True):
                wrapped_request_data = {"data": json.dumps(data),
                                        "clientKeyDetailsId": 1}
            else:
                wrapped_request_data = json.loads(data)
        response = request_method_function(url, wrapped_request_data,
                                           format='json', **header_parameters)
        self._assert_snapshots(response)
        return response

    def _assert_snapshots(self, response):
        self.assert_match_snapshot(response.status_code, name='status')
        try:
            response_content = json.loads(response.content)
        except ValueError:
            response_content = response.content.strip()
        self.assert_match_snapshot(response_content, name='body')

        from django.conf import settings
        mock_x_ib_request_id = getattr(settings, 'MOCK_X_IB_REQUEST_ID')
        if "x-ib-request-id" in response._headers and mock_x_ib_request_id:
            response._headers["x-ib-request-id"] = (
                'X-IB-REQUEST-ID', '8324199f578948078718d7291f3cb514'
            )

        response._headers = self._sort_response_headers(response._headers)
        self.assert_match_snapshot(response._headers, name='header_params')

    @staticmethod
    def _sort_response_headers(response_headers):
        from collections import OrderedDict
        response_headers = OrderedDict(sorted(response_headers.items()))

        for attr, attr_values in list(response_headers.items()):
            if attr == 'allow':
                response_headers.pop(attr)
            else:
                response_headers[attr] = sorted(attr_values)

        return response_headers

    def tearDown(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from oauth2_provider.models import Application
        User.objects.all().delete()
        Application.objects.all().delete()


class DiscoverRunner(TestRunner):
    def __init__(self, snapshot_update=False, **kwargs):
        super(DiscoverRunner, self).__init__(**kwargs)
        uTestCase.snapshot_should_update = snapshot_update
