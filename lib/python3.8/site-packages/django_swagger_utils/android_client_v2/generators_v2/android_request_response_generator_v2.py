from django.template import Template, Context

import collections
from django_swagger_utils.android_client_v2.generators_v2.android_generator_v2 import AndroidGeneratorV2

class AndroidRequestResponseGeneratorV2(AndroidGeneratorV2):
    # When the req_parameters is initialized here, it gives an error. TODO: Check why.
    # req_parameters = {}
    # TODO : Support only available for single array req/res body. If double or more, this won't work.
    #        Change check_if_req_is_array method in android_generator.py
    def __init__(self, app_name, parser, path, method_props, paths, base_path):
        AndroidGeneratorV2.__init__(self, app_name, parser, paths, base_path)
        self.path = path
        self.method_props = method_props
        self.req_name = self.snake_to_camel_case(method_props.get("operationId"))
        self.req_parameters = {}
        self.res_parameters = {}
        self.req_is_array = ""
        self.res_is_array = ""
        self.path_params = {}
        self.query_params = {}

    def generate_android_request_response_v2(self):
        # self.req_parameters.clear()
        """
        this generates requests and responses for a particular api in java format

        :return:
        """
        #self.req_parameters.clear()

        self.path_params = self.get_params_from_properties(self.path, "path")[0]
        self.query_params = self.get_params_from_properties(self.path, "query")[0]
        self.path_params = self.merge_dicts(self.path_params, self.get_params_from_properties(self.method_props, "path")[0])
        self.query_params = self.merge_dicts(self.query_params, self.get_params_from_properties(self.method_props, "query")[0])
        if self.path_params:
            self.path_params = collections.OrderedDict(sorted(self.path_params.items()))
            self.path_params = self.convert_data_types_to_java_format_v2(self.path_params)
        if self.query_params:
            self.query_params = collections.OrderedDict(sorted(self.query_params.items()))
            self.query_params = self.convert_data_types_to_java_format_v2(self.query_params)

        self.req_parameters = self.get_request_parameters(self.path)
        self.req_parameters = self.merge_dicts(self.req_parameters, self.get_request_parameters(self.method_props))
        self.res_parameters = self.get_response_parameters(self.method_props)

        req_is_single_model = self.check_if_request_is_single_model(self.req_parameters)
        android_model = ""
        if req_is_single_model:
            android_model = self.get_model_name_from_parameter(self.req_parameters)
            android_model = android_model[0].upper() + android_model[1:]

        res_is_single_model = self.check_if_request_is_single_model(self.res_parameters)
        android_res_model = ""
        if res_is_single_model:
            android_res_model = self.get_model_name_from_parameter(self.res_parameters)
            android_res_model = android_res_model[0].upper() + android_res_model[1:]

        self.regenerate_model_if_array_v2(self.req_parameters)
        self.regenerate_model_if_array_v2(self.res_parameters)

        self.req_parameters = self.generate_nested_models_v2(self.req_parameters, self.base_path + "/models/requests/" + self.req_name)
        self.res_parameters = self.generate_nested_models_v2(self.res_parameters, self.base_path + "/models/responses/" + self.req_name)

        self.req_parameters_are_optional = False
        if self.check_if_parameters_are_optional_v2(self.req_parameters):
            self.req_parameters_are_optional = True
        self.res_parameters_are_optional = False
        if self.check_if_parameters_are_optional_v2(self.res_parameters):
            self.res_parameters_are_optional = True

        if (self.check_if_request_is_array_v2(self.req_parameters)):
            self.req_is_array = "[]"

        self.req_parameters = self.get_type_dict_only(self.req_parameters)
        self.res_parameters = self.get_type_dict_only(self.res_parameters)

        self.req_parameters = collections.OrderedDict(sorted(self.req_parameters.items()))
        self.res_parameters = collections.OrderedDict(sorted(self.res_parameters.items()))

        if (self.check_if_response_is_array_v2(self.method_props)):
            self.res_is_array = ".List"

        # Generating content and writing it into files
        self.req_parameters = self.convert_data_types_to_java_format_v2(self.req_parameters)
        self.res_parameters = self.convert_data_types_to_java_format_v2(self.res_parameters)
        #self.req_parameters = sorted(self.req_parameters.items())
        #self.res_parameters = sorted(self.res_parameters.items())

        self.req_parameters, req_is_single_type_array = self.filter_single_type_array(self.req_parameters)
        self.res_parameters, res_is_single_type_array = self.filter_single_type_array(self.res_parameters)

        if self.req_parameters and not req_is_single_model:
            android_request_file_content = self.android_request_file_contents_v2()
            self.write_android_file(android_request_file_content, "request")

        if self.res_parameters and not res_is_single_model:
            android_response_file_content = self.android_response_file_contents_v2()
            self.write_android_file(android_response_file_content, "response")

        android_spice_request_file_content = self.android_spice_request_file_contents_v2(android_model, android_res_model, req_is_single_type_array=req_is_single_type_array, res_is_single_type_array=res_is_single_type_array)

        self.write_android_spice_request_file_v2(android_spice_request_file_content)

    def android_request_file_contents_v2(self):
        """
        the dictionary is formed which has import statements and requests
        a java code is created with template in android_request.py in templates folder

        :return:
        """
        android_request_context = {
            "android_common_models_import_statement": self.get_import_statement_from_path_v2(
                self.base_path + "/models/common"),
            "android_import_statement": self.get_import_statement_from_path_v2(
                self.base_path + "/models/requests/" + self.req_name),
            "req_parameters": list(self.req_parameters.items()),
            "android_request_camel_case_name": self.req_name,
            "android_request_is_array": self.req_is_array,
            "android_req_parameters_are_optional": self.req_parameters_are_optional
        }
        from django_swagger_utils.android_client_v2.templates_v2.android_request import ANDROID_REQUEST
        android_request_template = Template(ANDROID_REQUEST)
        context = Context(android_request_context)
        return android_request_template.render(context)

    def android_response_file_contents_v2(self):
        """
        the dictionary is formed which has import statements and responses
        a java code is created with template in android_response.py in templates folder
        :return:
        """
        android_response_context = {
            "android_common_models_import_statement" : self.get_import_statement_from_path_v2(self.base_path + "/models/common"),
            "android_import_statement": self.get_import_statement_from_path_v2(
                self.base_path + "/models/responses/" + self.req_name),
            "res_parameters": list(self.res_parameters.items()),
            "android_response_camel_case_name": self.req_name,
            "android_res_is_array" : self.res_is_array,
            "android_res_parameters_are_optional": self.res_parameters_are_optional
        }
        from django_swagger_utils.android_client_v2.templates_v2.android_response import ANDROID_RESPONSE
        android_request_template = Template(ANDROID_RESPONSE)
        context = Context(android_response_context)
        return android_request_template.render(context)

    def android_spice_request_file_contents_v2(self, android_model = "", android_res_model="", req_is_single_type_array="", res_is_single_type_array=""):
        """
       a dictionary is formed which has imports requests and responses
       a  java code is created with the template in android_spice_request.py        :param android_model:
       :param android_res_model:
       :param req_is_single_type_array:
       :param res_is_single_type_array:
       :return:
       """
        android_spice_request_context = {
            "android_import_statement": self.get_import_statement_from_path_v2(self.base_path),
            "android_spice_request_variable_name": self.get_variable_name_for_definition(self.req_name),
            "android_spice_request_camel_case_name": self.req_name,
            "android_path_parameters": list(self.path_params.items()),
            "android_query_parameters": list(self.query_params.items()),
            "android_req_is_array": self.req_is_array,
            "android_res_is_array": self.res_is_array,
            "android_app_name": self.snake_to_camel_case(self.app_name),
            "android_req_parameters": self.req_parameters,
            "android_res_parameters": self.res_parameters,
            "android_model" : android_model,
            "android_res_model": android_res_model,
            "android_req_is_single_type_array": req_is_single_type_array,
            "android_res_is_single_type_array": res_is_single_type_array
        }
        from django_swagger_utils.android_client_v2.templates_v2.android_spice_request import ANDROID_SPICE_REQUEST

        android_spice_request_template = Template(ANDROID_SPICE_REQUEST)

        context = Context(android_spice_request_context)
        return android_spice_request_template.render(context)

    def write_android_file(self, android_file_content, file_type):
        """
       the corresponding java source file for requests and response is created in models directory
       in Requests or Responses sub-directory
       :param android_file_content:
       :param file_type:
       :return:
       """
        android_file_path = self.base_path + "/models/" + file_type + "s/" + self.req_name + "/" + self.req_name + self.snake_to_camel_case(file_type) + ".java"
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(android_file_content, android_file_path, False)

    def write_android_spice_request_file_v2(self, android_file_content):
        """
         the corresponding SpiceRequest class file is created for each api
         in network directory in SpiceRequests sub-directory

        :param android_file_content:
        :return:
        """
        android_file_path = self.base_path + "/network/spice_requests/" + self.req_name + "SpiceRequest.java"
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(android_file_content, android_file_path, False)
