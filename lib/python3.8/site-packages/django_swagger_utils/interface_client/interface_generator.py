from django.template import Template, Context

from django_swagger_utils.core.utils.case_convertion import to_camel_case
from django_swagger_utils.core.utils.write_to_file import write_to_file


class InterfaceGenerator(object):
    def __init__(self, app_name, parser, paths, override):
        self.app_name = app_name
        self.parser = parser
        self.paths = paths
        self.override = override

    def generate_interfaces(self, service_interface_path=None):
        """
        driver method. calls other methods to generate the interfaces.
        :return:
        """

        if service_interface_path is None:
            service_interface_path = self.paths['service_interface_path']

        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists

        if check_path_exists(service_interface_path) and not \
           self.override:
            return
        context_dict = {
            'app_name_capital': to_camel_case(self.app_name.capitalize()),
            'app_name_upper': self.app_name.upper(),
            'app_name': self.app_name,
            'author': 'iB'
        }
        function_list = []
        for path, path_body in list(self.parser.paths().items()):
            for each_method in list(path_body.keys()):
                if each_method in ['get', 'put', 'delete', 'post', 'update']:
                    inner_body = path_body[each_method]
                    operation_id = inner_body['operationId']
                    if inner_body.get("x-interface-required", False):
                        continue
                    functions = (operation_id, each_method.upper(), path)
                    function_list.append(functions)
        context_dict['functions'] = function_list
        from django_swagger_utils.interface_client.templates \
            .interface_template import interface_template
        template = Template(interface_template)
        data = template.render(Context(context_dict))
        write_to_file(data, service_interface_path)
