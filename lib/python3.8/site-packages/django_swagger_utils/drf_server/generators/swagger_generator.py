
class SwaggerGenerator(object):
    def __init__(self, parser, paths, app_name):
        self.parser = parser
        self.paths = paths
        self.app_name = app_name

    def generate_request_response(self):

        from django_swagger_utils.drf_server.generators.request_response import \
            RequestResponseGenerator
        req_res = RequestResponseGenerator(self.parser.security_definitions(),
                                           self.parser.consumes(),
                                           self.parser.produces(),
                                           self.parser.security(), self.paths)
        req_res.generate_request_response_package()

    def generate_definitions(self):
        for def_name, definition in list(self.parser.definitions().items()):
            from django_swagger_utils.core.generators.swagger_sample_schema import \
                SwaggerSampleSchema
            swagger_sample_json = SwaggerSampleSchema(
                self.parser.definitions(), definition)
            is_ref_to_array = False
            if '$ref' in definition:
                ref = definition['$ref']
                ref = ref.split('/')[2]
                ref_def = swagger_sample_json.get_definition_json(ref)
                if type(ref_def) is list:
                    is_ref_to_array = True

            base_path = self.paths["definitions_serializers_base_dir"]

            from django_swagger_utils.drf_server.generators.serializer_generator import \
                SerializerGenerator
            serializer_generator = SerializerGenerator(
                schema_properties=definition, serializer_name=def_name,
                base_path=base_path, paths=self.paths)
            serializer_generator.generate_serializer_file(
                to_file=True,
                is_ref_to_array=is_ref_to_array)

    def generate_parameters(self):
        for parameter_name, parameter in list(self.parser.parameters().items()):
            from django_swagger_utils.drf_server.generators.parameters_generator import \
                ParametersGenerator
            parameter_generator = ParametersGenerator(
                parameter_name.replace(' ', ''), parameter, self.paths,
                self.parser)
            parameter_generator.generate_parameter_file()

    def generate_responses(self):
        for response_name, response in list(self.parser.responses().items()):
            base_path = self.paths["global_response_dir"] + "/" + response_name

            from django_swagger_utils.drf_server.generators.response_generator import \
                ResponseGenerator
            response_generator = ResponseGenerator(self.paths, response,
                                                   response_name,
                                                   self.parser.definitions(),
                                                   base_path,
                                                   self.parser.responses())
            response_generator.generate_response_file()

    def generate_paths(self):
        pass

    def generate_urls(self):

        from django_swagger_utils.drf_server.generators.url_generator import \
            URLGenerator
        url_generator = URLGenerator(self.app_name, self.paths, self.parser)
        url_generator.configure()
        url_generator.generate_url()
        url_generator.generate_view_environment()

    def generate_test_case(self, operation_id, tcn, snapshot=False):
        is_found = False
        for path_name, path in list(self.parser.paths().items()):
            from django_swagger_utils.drf_server.generators.path_generator import \
                PathGenerator

            path_generator = PathGenerator(self.app_name, self.paths, path,
                                           path_name, self.parser)
            is_found = path_generator.generate_new_testcase(operation_id, tcn,
                                                            snapshot=snapshot)
            if is_found:
                return

        if not is_found:
            from colored import fg, attr
            print(
                '{}{}{}\'{}\' not found in apps. Please provide correct operation id.'.format(
                    fg(1), attr(1), attr(4), operation_id))
        return

    def generate_view_environments(self):
        pass
