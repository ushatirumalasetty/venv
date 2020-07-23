from django_swagger_utils.core.utils.write_to_file import write_to_file
from .conf import render


class ParametersGenerator(object):
    base_path = ""

    def __init__(self, parameter_name, parameter, paths, parser):
        self.parameter_name = parameter_name
        self.parameter = parameter
        self.paths = paths
        self.parser = parser

    def set_base_path(self):
        self.base_path = self.paths["global_parameters_dir"] + "/" + self.parameter_name

    def generate_parameter_file(self):
        self.set_base_path()
        param_context_properties = self.get_param_context_properties(self.parameter)
        parameter_file_contents = self.parameter_file_contents(param_context_properties)
        self.write_parameter_file(parameter_file_contents, param_context_properties["param_name"])

    def get_param_context_properties(self, param):
        if param["in"] == "query":

            from django_swagger_utils.drf_server.fields.query_parameter_field import query_param_field
            param_context_properties = query_param_field(param, parameter_key_name=self.parameter_name)
        elif param["in"] == "header":

            from django_swagger_utils.drf_server.fields.header_parameter_field import header_field
            param_context_properties = header_field(param, parameter_key_name=self.parameter_name)
        elif param["in"] == "path":

            from django_swagger_utils.drf_server.fields.path_parameter_field import path_param_field
            param_context_properties = path_param_field(param, parameter_key_name=self.parameter_name)
        # elif param["in"] == "formData":
        #     from common.swagger.utils.fields.form_parameter_field import form_param_field
        #     param_context_properties = form_param_field(param, parameter_key_name=self.parameter_name)
        elif param["in"] == "body":

            from django_swagger_utils.drf_server.fields.body_field import body_field
            param_context_properties = body_field(param, self.paths, self.base_path, self.parameter_name,
                                                  swagger_definitions=self.parser.definitions())
        else:
            raise Exception("invalid value %s for parameter in" % param["in"])
        return param_context_properties

    @staticmethod
    def get_object_properties(prop_name, schema_properties, paths, base_path):

        from django_swagger_utils.drf_server.generators.serializer_generator import SerializerGenerator
        serializer_generator = SerializerGenerator(schema_properties=schema_properties, base_path=base_path,
                                                   serializer_name=prop_name, paths=paths)
        context_properties = serializer_generator.generate_serializer_file(to_file=True)
        return context_properties

    @staticmethod
    def parameter_file_contents(parameter_context):
        return render('parameters.j2', parameter_context)

    def write_parameter_file(self, parameter_file_contents, param_name):
        serializer_file_path = self.base_path + "/" + param_name + "Parameter.py"
        write_to_file(parameter_file_contents, serializer_file_path)
