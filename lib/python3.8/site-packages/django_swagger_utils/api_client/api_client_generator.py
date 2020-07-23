import os
from django.template import Template, Context

from django_swagger_utils.core.utils.case_convertion import to_camel_case
from django_swagger_utils.core.utils.write_to_file import write_to_file


class APIClientGenerator(object):
    def __init__(self, app_name, parser, paths):
        self.app_name = app_name
        self.parser = parser
        self.paths = paths

    def generate(self):
        """
        driver method. calls other methods to generate the interfaces.
        :return:
        """
        context_dict = {
            'app_name_capital': to_camel_case(self.app_name.capitalize()),
            'app_name_upper': self.app_name.upper(),
            'app_name': self.app_name,
            'author': 'iB'
        }
        endpoints_list = []

        from django_swagger_utils.drf_server.generators.path_generator import \
            PathGenerator
        for path_name, path_body in list(self.parser.paths().items()):
            path_generator = PathGenerator(self.app_name, self.paths,
                                           path_body, path_name, self.parser)

            for each_method in list(path_body.keys()):

                if each_method in ['get', 'put', 'delete', 'post', 'update']:
                    inner_body = path_body[each_method]
                    operation_id = inner_body['operationId']

                    if inner_body.get("x-interface-required", False):
                        continue

                    path_generator.group_name = \
                        inner_body.get('group_name', '')
                    endpoint_dict = path_generator\
                        .get_api_client_dict(operation_id)
                    endpoint_dict["summary"] = inner_body.get("summary", "")
                    endpoint_dict["description"] = inner_body.get("description", "")
                    endpoints_list.append(endpoint_dict)
        context_dict['endpoints'] = endpoints_list
        from django_swagger_utils.api_client.templates \
            .api_client_template import api_client_template
        template = Template(api_client_template)
        data = template.render(Context(context_dict))
        write_to_file(data, self.paths['client_api_client_path'])
