
from io import open
__author__ = 'tanmay.ibhubs'


class SwaggerSpec(object):
    def __init__(self, access_token, organization_id, project_id, app_id, service_url, paths):
        """

        :param access_token:
        :param organization_id:
        :param project_id:
        :param app_id:
        :param service_url:
        :param paths:

        Initialize the Swaager spec service with configuration details
        """
        self.access_token = "Bearer " + access_token
        self.organization_id = organization_id
        self.project_id = project_id
        self.app_id = app_id
        self.service_url = service_url
        self.app_name = ''
        self.paths = paths

    def verify_app(self):
        """
        If app name from swagger spec was not in swagger_apps
        it will print error and return

        :return:
        """
        import requests
        from django.conf import settings
        from .interface_exception_handler import handle_interface_exception
        endpoint = 'organization/%s/app/%s/' % (self.organization_id, self.app_id)
        api_url = self.service_url + endpoint

        response = requests.get(url=api_url,
                                headers={"content-type": "application/json", "authorization": self.access_token})
        import json
        response_body = json.loads(response.content)
        if 'app_id' not in response_body:
            handle_interface_exception(response_body)
        app = response_body.get('name', '')
        self.app_name = app
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        if app not in swagger_apps:
            from colored import fg, attr
            print('{}{}{}\'{}\' not found in swagger_apps. '
                  'Please add it first.'.format(fg(1), attr(1), attr(4), app))
            return False
        return True

    def get_spec_file(self):
        """
        gets the specfile based on app, project and organization
        if any error, prints it and returns False

        If no error comes, it returns True
        :return:
        """
        import requests
        from .interface_exception_handler import handle_interface_exception
        endpoint = 'organization/%s/projects/%s/apps/%s/spec_file/' % (
            self.organization_id, self.project_id, self.app_id)
        api_url = self.service_url + endpoint
        response = requests.post(url=api_url,
                                 headers={"content-type": "application/json", "accepts": "application/json",
                                          "authorization": self.access_token})
        import json
        if not response:
            from colored import fg, attr
            print('{}{}{}Spec file could not be generated! :('.format(
                fg(1), attr(1), attr(4)))
            return False
        response_body = json.loads(response.content)
        if 'spec_file' not in response_body:
            handle_interface_exception(response.content)
            return

        spec_file = json.loads(response_body['spec_file'])


        return spec_file

    def sync_spec_file(self):
        """
        Updates (overwrites) the spec file in project with the one from server

        :return:
        """
        import requests
        from .interface_exception_handler import handle_interface_exception
        endpoint = 'organization/%s/projects/%s/apps/%s/spec_file/' % (
            self.organization_id, self.project_id, self.app_id)
        api_url = self.service_url + endpoint
        response = requests.post(url=api_url,
                                 headers={"content-type": "application/json", "accepts": "application/json",
                                          "authorization": self.access_token})
        import json
        if not response:
            from colored import fg, attr
            print('{}{}{}Spec file could not be generated! :('.format(
                fg(1), attr(1), attr(4)))
            return False
        response_body = json.loads(response.content)
        if 'spec_file' not in response_body:
            handle_interface_exception(response.content)

        spec_file = json.loads(response_body['spec_file'])

        api_spec_file = open(self.paths["api_specs_json"], 'w+')
        api_spec_file.write(json.dumps(spec_file))
        api_spec_file.close()

        return
