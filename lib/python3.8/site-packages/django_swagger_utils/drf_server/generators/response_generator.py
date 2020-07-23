# coding=utf-8
from .conf import render

from django_swagger_utils.drf_server.fields.boolean_field import boolean_field
from django_swagger_utils.drf_server.fields.integer_field import integer_field
from django_swagger_utils.drf_server.fields.number_field import number_field
from django_swagger_utils.drf_server.fields.string_field import string_field


class ResponseGenerator(object):
    def __init__(self, paths, response, response_name, swagger_definitions,
                 base_path, swagger_response,
                 write_file=True):
        self.paths = paths
        self.response = response
        self.response_name = response_name
        self.swagger_definitions = swagger_definitions
        self.base_path = base_path
        self.swagger_responses = swagger_response
        self.write_file = write_file

    def get_camel_case_response_name(self):

        from django_swagger_utils.core.utils.case_convertion import \
            to_camel_case
        return to_camel_case(self.response_name)

    def generate_response_file(self):
        response_ref = self.response.get("$ref", None)
        if response_ref:
            self.setup_response_from_ref(response_ref)

        response_context_dict = self.get_response_context_dict()
        self.write_response_file(response_context_dict)
        return response_context_dict

    def write_response_file(self, context_properties):

        response_file_path = self.base_path + "/" + self.response_name + "Response.py"
        response_file_contents = self.get_response_file_content(
            context_properties)

        if self.write_file:
            from django_swagger_utils.core.utils.write_to_file import \
                write_to_file
            write_to_file(response_file_contents, response_file_path)

    def get_response_context_dict(self):
        response_context_properties = self.get_response_context_properties()
        response_headers_context_properties = self.get_response_headers_context_properties()
        response_context_properties.update(response_headers_context_properties)
        return response_context_properties

    def get_response_context_properties(self):
        context_properties = {
            "response_name_camel_case": self.get_camel_case_response_name(),
            "response_data": "",
            "response_data_no_indent": "",
            "response_serializer": "",
            "response_serializer_import_str": "",
            "response_serializer_array": "\"\""
        }

        response_schema = self.response.get("schema", None)
        if response_schema:

            from django_swagger_utils.core.generators.swagger_sample_schema import \
                SwaggerSampleSchema
            swagger_sample_json = SwaggerSampleSchema(self.swagger_definitions,
                                                      response_schema)
            response_data = swagger_sample_json.get_data_dict()
            context_properties["response_data"] = response_data
            # checks if reference
            to_file = True
            if '$ref' in response_schema:
                to_file = False

            if isinstance(response_data, dict) or \
                (isinstance(response_data, list) and not isinstance(
                    response_data[0], list)):
                object_properties = self.get_object_properties(
                    schema_properties=response_schema, to_file=to_file)
                context_properties[
                    "response_data"] = swagger_sample_json.to_json(indent=4)
                context_properties[
                    "response_data_no_indent"] = swagger_sample_json.to_json(
                    indent=0)
                context_properties["response_serializer"] = object_properties[
                    "field_string"]
                context_properties["response_serializer_import_str"] = \
                    object_properties["serializer_import_str"]
                context_properties["response_serializer_array"] = \
                    object_properties["is_array_serializer"]

        return context_properties

    def get_object_properties(self, schema_properties, to_file=True):

        from django_swagger_utils.drf_server.generators.serializer_generator import \
            SerializerGenerator
        serializer_generator = SerializerGenerator(
            schema_properties=schema_properties, base_path=self.base_path,
            serializer_name=self.response_name, paths=self.paths)
        context_properties = serializer_generator.generate_serializer_file(
            to_file=to_file)
        return context_properties

    def get_response_headers_context_properties(self):
        context_properties = {
            "response_headers_serializer": "",
            "response_headers_serializer_import_str": "",
            "response_headers_example_params": {}
        }
        headers = self.response.get("headers", None)
        if headers:
            package_import_str, response_headers_serializer, response_header_example_params = \
                self.process_headers_serializer_data(headers)
            context_properties[
                "response_headers_serializer_import_str"] = "from %s import %s" % (
                package_import_str, response_headers_serializer
            )
            context_properties[
                "response_headers_serializer"] = response_headers_serializer
            context_properties[
                "response_headers_example_params"] = response_header_example_params
        return context_properties

    def process_headers_serializer_data(self, headers):

        response_header_serializer_fields = {
            "required_params": [],
            "optional_params": [],
            "params": {},
            "example_params": {},
            "object_params": {},
            "serializer_camel_case_name": self.get_camel_case_response_name() + "Headers"
        }

        for header_name, each_header, in list(headers.items()):
            each_header_properties = self.header_field(each_header,
                                                       header_name)
            header_name = header_name.replace("-", "_")
            response_header_serializer_fields["params"][
                header_name] = each_header_properties
            response_header_serializer_fields["example_params"][header_name] = \
                each_header_properties["param_example"]
            response_header_serializer_fields["required_params"].append(
                header_name)

        response_headers_serializer = self.get_camel_case_response_name() + "HeadersSerializer"
        serializer_path = self.base_path + "/" + response_headers_serializer + ".py"

        from django_swagger_utils.core.utils.convert_path_to_package_str import \
            convert_path_to_package_str
        package_import_str = convert_path_to_package_str(serializer_path,
                                                         self.paths[
                                                             'base_dir'])

        self.write_response_headers_file(serializer_path,
                                         response_header_serializer_fields)

        return package_import_str, response_headers_serializer, \
               response_header_serializer_fields["example_params"]

    def write_response_headers_file(self, serializer_path,
                                    response_header_serializer_fields):
        response_headers_serializer_file_contents = self.get_response_header_file_content(
            response_header_serializer_fields)

        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(response_headers_serializer_file_contents,
                      serializer_path)

    @staticmethod
    def get_response_file_content(response_context):
        return render('responses.j2', response_context)

    @staticmethod
    def get_response_header_file_content(serializer_context):
        return render('serializers.j2', serializer_context)

    def header_field(self, header, header_name):

        field_properties = {
            "field_string": "",
            "param_example": ""
        }

        header_type = header.get("type", None)

        if not header_type:
            raise Exception(
                "'type' not defined for header field :'%s' - %s" % (
                    header_name, self.response_name))
        if header_type == "integer":
            field_properties["field_string"], field_properties[
                "param_example"] = \
                integer_field(header, return_example=True)
        elif header_type == "number":
            field_properties["field_string"], field_properties[
                "param_example"] = \
                number_field(header, return_example=True)
        elif header_type == "string":
            field_properties["field_string"], field_properties[
                "param_example"] = \
                string_field(header, return_example=True)
        elif header_type == "boolean":
            field_properties["field_string"], field_properties[
                "param_example"] = \
                boolean_field(header, return_example=True)
        elif header_type == "array":
            collection_format = header.get("collectionFormat", "csv")
            field_properties["field_string"], field_properties[
                "param_example"] = \
                self.get_array_field(header.get("items"), header_name,
                                     collection_format, )
        else:
            raise Exception("Invalid value for type of header field")
        return field_properties

    def get_array_field(self, array_header_field, array_name,
                        collection_format):
        array_header_field_type = array_header_field.get("type", None)

        from django_swagger_utils.drf_server.utils.server_gen.collection_fromat_to_separator import \
            collection_format_to_separator
        separator = collection_format_to_separator(collection_format)
        if not array_header_field:
            raise Exception(
                "property 'type' not defined for array filed : '%s' " % array_name)
        if array_header_field_type == "integer":
            child_str, example = integer_field(array_header_field,
                                               return_example=True)
        elif array_header_field_type == "number":
            child_str, example = number_field(array_header_field,
                                              return_example=True)
        elif array_header_field_type == "string":
            child_str, example = string_field(array_header_field,
                                              return_example=True)
        elif array_header_field_type == "boolean":
            child_str, example = boolean_field(array_header_field,
                                               return_example=True)
        elif array_header_field_type == "array":
            inner_collection_format = array_header_field.get(
                "collectionFormat", "csv")
            inner_array_header_field = array_header_field.get("items")
            child_str, example = self.get_array_field(inner_array_header_field,
                                                      array_name,
                                                      inner_collection_format)
        else:
            raise Exception(
                "Unsupported array field type: choices [integer, string, number, boolean, array]")
        header_field_serializer_field = "CollectionFormatField(separator='%s', child=%s)" % (
            separator, child_str)
        return header_field_serializer_field, [example]

    def setup_response_from_ref(self, response_ref):

        response_ref_split = response_ref.split("#/responses/")
        self.response_name = response_ref_split[1]
        self.write_file = False
        self.base_path = self.paths[
                             "global_response_dir"] + "/" + self.response_name
        self.response = self.swagger_responses.get(self.response_name)
