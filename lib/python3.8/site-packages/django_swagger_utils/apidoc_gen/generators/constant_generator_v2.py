__author__ = 'tanmay.ibhubs'


class ConstantGeneratorV2(object):
    def __init__(self, parser, filename):
        self.parser = parser
        self.classes = list()
        self.filename = filename
        self.model_list = list()

    @staticmethod
    def get_camel_case(string):
        each_key_parts = string.split("_")

        def upper(string):
            return string[0].upper() + string[1:]

        return ''.join(map(upper, each_key_parts))

    def constant_gen(self):
        # write headers and imports
        self.generate_for_definitions()
        self.generate_for_parameters()
        self.generate_for_responses()
        self.generate_for_paths()
        self.write_to_file()

    def generate_for_definitions(self):
        definitions = self.parser.definitions()
        for key, schema in list(definitions.items()):
            if 'allOf' in schema:
                self.parse_all_of(schema)
            else:
                schema_type = schema.get('type')
                if schema_type == 'object':
                    self.object_file_write(schema)
                elif schema_type == 'array':
                    self.array_file_write(schema, key)

    def generate_for_parameters(self):
        parameters = self.parser.parameters()
        for key, parameter_body in list(parameters.items()):
            schema = parameter_body.get('schema')
            if not schema:
                continue
            if 'allOf' in schema:
                self.parse_all_of(schema)
            else:
                schema_type = schema.get('type')
                if schema_type == 'object':
                    self.object_file_write(schema)
                elif schema_type == 'array':
                    self.array_file_write(schema, key)

    def generate_for_responses(self):
        responses = self.parser.responses()
        for key, response_body in list(responses.items()):
            schema = response_body.get('schema')
            if not schema:
                continue
            if 'allOf' in schema:
                self.parse_all_of(schema)
            else:
                schema_type = schema.get('type')
                if schema_type == 'object':
                    self.object_file_write(schema)
                elif schema_type == 'array':
                    self.array_file_write(schema, key)

    def generate_for_paths(self):
        paths = self.parser.paths()
        for path, api in list(paths.items()):
            for api_method_key, api_content in list(api.items()):
                if api_method_key == 'parameters':
                    self.parse_path_parameters(api_content)
                else:
                    self.parse_path(api_content)

    def primitive_file_write(self, schema, each_key):

        enum_value = schema.get("enum")
        if not enum_value:
            return
        class_name = self.get_camel_case(each_key)
        if class_name not in self.classes:
            self.classes.append(class_name)
            variables = []
            for each in enum_value:
                variables.append(each)
            model = (class_name, variables,)
            self.model_list.append(model)
        else:
            title = 'Multiple definition for key \'{key}\' found. Use \'allOf\'. \n'.format(
                key=each_key)
            from colored import fg, attr
            print('{}{}{}WARNING: '.format(fg(3), attr(1), attr(4)), end=title)

    def object_file_write(self, schema):

        properties_value = schema.get("properties")
        for each_key, each_value in list(properties_value.items()):
            if 'allOf' in each_value:
                self.parse_all_of(each_value)
            elif '$ref' in each_value:
                pass
            else:
                value_type = each_value.get('type')
                if value_type == 'string' and 'enum' in list(each_value.keys()):
                    self.primitive_file_write(each_value, each_key)
                elif value_type == 'array':
                    self.array_file_write(each_value, each_key)
                elif value_type == 'object':
                    self.object_file_write(each_value)

    def array_file_write(self, items_schema, schema_key):
        schema_key = schema_key + '_array'
        items_values = items_schema.get("items")
        items_value_type = items_values.get('type')
        if 'allOf' in items_values:
            self.parse_all_of(items_values)
        else:
            if items_value_type == 'string':
                self.primitive_file_write(items_values, schema_key)
            elif items_value_type == 'object':
                self.object_file_write(items_values)

    def parse_all_of(self, schema):
        all_of_schema = schema['allOf']
        for sub_schema in all_of_schema:
            sub_schema_type = sub_schema.get('type')
            if sub_schema_type == 'object':
                self.object_file_write(sub_schema)

    def parse_path_parameters(self, parameters):
        if not parameters:
            return
        for parameter_body in parameters:
            schema = parameter_body.get('schema')
            if not schema:
                continue
            key = parameter_body['name']
            if 'allOf' in schema:
                self.parse_all_of(schema)
            else:
                schema_type = schema.get('type')
                if schema_type == 'object':
                    self.object_file_write(schema)
                elif schema_type == 'array':
                    self.array_file_write(schema, key)

    def parse_path_responses(self, responses, operation_id):
        if not responses:
            return
        for response_key, response_body in list(responses.items()):
            key = operation_id + response_key
            schema = response_body.get('schema')
            if not schema:
                continue
            if 'allOf' in schema:
                self.parse_all_of(schema)
            else:
                schema_type = schema.get('type')
                if schema_type == 'object':
                    self.object_file_write(schema)
                elif schema_type == 'array':
                    self.array_file_write(schema, key)

    def parse_path(self, api_content):
        operation_id = api_content.get('operationId')
        parameters = api_content.get('parameters')
        responses = api_content.get('responses')

        self.parse_path_parameters(parameters)
        self.parse_path_responses(responses, operation_id)

    def write_to_file(self):
        from django.template.base import Template
        from django.template.context import Context
        from django_swagger_utils.core.utils.write_to_file import write_to_file

        from django_swagger_utils.apidoc_gen.template.constant_template import \
            models
        enum_template = Template(models)
        classes = {
            'classes': self.model_list
        }
        write_to_file(enum_template.render(Context(classes)),
                      self.filename,
                      False)
