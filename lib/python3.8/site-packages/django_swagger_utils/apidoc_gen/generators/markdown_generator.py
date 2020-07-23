
import json
import os
from django_swagger_utils.core.generators.generator import Generator
from django_swagger_utils.core.generators.swagger_sample_schema import SwaggerSampleSchema
from io import open


class MarkdownGenerator(Generator):

    def __init__(self, app_name, parser, paths, base_path):
        Generator.__init__(self, app_name, parser, paths, base_path)

    def create_documentation(self, filename):
        f = open(filename, "a")
        definitions = self.parser.definitions()
        # only the first links of the apps present in django-swagger-utils

        api_list = list(self.parser.paths().items())
        for api_obj in api_list:
            api_path = api_obj[0]
            api = api_obj[1]

            for api_method, api_content in list(api.items()):

                if (api_method == 'get') or (api_method == 'post') or (api_method == 'delete') or (api_method == 'put'):
                    # get the operation_id of the app
                    operation_id = api_content.get("operationId")
                    f.write("### " + operation_id + "\n\n")

                    # get the api_method and api_path of the app
                    api_method_upper = api_method.upper()
                    f.write(
                        "* **" + api_method_upper + "** - \n\t * " + "/api/" +
                        self.app_name + api_path + "\n" + "-----" + "\n\n")

                    # get the api_description of the app
                    if api_content.get("description"):
                        api_description = api_content.get("description")
                        f.write("> **" + "Description" + "**:" + api_description + "\n")

                    # get the api_summary of the app
                    api_summary = api_content.get("summary", None)
                    if api_summary is not None:
                        f.write("> **" + "Summary" + "**: " + api_summary + "\n\n")

                    # get the list of all the path_types of parameters
                    path_types_lst_1 = self.get_path_types(api_content)
                    path_types_lst_2 = self.get_path_types(api)
                    path_types_list = path_types_lst_1 + path_types_lst_2

                    # get the table of all types of parameters
                    if path_types_list != []:
                        f.write("#### " + "Parameters:" + "\n")
                        f.write("| " + "Parameter Name" + " | " + "Type" + " | " + "Position" + " |" + "Required" + " |"
                                + "\n")
                        f.write("| - | - | - | - |" + "\n")

                        for each_param in path_types_list:
                            self.get_params(api_content, each_param, f, api)
                        f.write("\n")

                    # get the request body of the app if it has any
                    if "body" in path_types_list:
                        self.print_body_parameters(definitions, api_content, f)

                    security_dict = self.parser.security_definitions()

                    f.write("#### " + "Security: " + "\n\n")
                    f.write("| " + "Security Name" + " | " + "Scopes" + " | " + "Type" + " | " + "\n")
                    f.write("| - | - | - |" + "\n")
                    self.get_security_scopes(api_content, security_dict, f)

                    # get the response of the app if it has any
                    f.write("#### " + "Response:" + "\n\n")
                    self.print_all_responses_res_schema(definitions, api_content, f)
                    f.write("-----" + "\n\n")
        f.close()
        return filename


    def get_params(self, api_content, path_type, f, dict2=""):
        counter = 1
        if "parameters" in api_content:
            parameters = api_content.get("parameters")
            for param in parameters:
                if "$ref" in param:
                    paramt_name = self.get_name_from_reference(param.get("$ref"))
                    for param_name, parameters in list(self.parser.parameters().items()):
                        required = ""

                        if (param_name == paramt_name) and (parameters.get("in") == path_type):
                            key = parameters.get("name")
                            value = parameters.get("type")
                            if value == None:
                                value = "json"
                            if parameters.get("required"):
                                required_bool = str(parameters.get("required"))
                            else:
                                required_bool = "False"
                            f.write("| " + key + ' | ' + value + ' | ' + path_type + ' | ' + required_bool + " |" + "\n")
                            counter += 1

                if ('in' in param) and (param.get("in") == path_type):
                    key = param.get("name")
                    value = param.get("type")
                    if value == None:
                        value = "json"
                    if param.get("required"):
                        required_bool = str(param.get("required"))
                    else:
                        required_bool = "False"
                    f.write('| ' + key + ' | ' + value + ' | ' + path_type + ' | ' + required_bool + " |" + "\n")
                    counter += 1

        if "parameters" in dict2:
            parameters = dict2.get("parameters")
            for param in parameters:
                if "$ref" in param:
                    paramt_name = self.get_name_from_reference(param.get("$ref"))
                    for param_name, parameters in list(self.parser.parameters().items()):
                        if (param_name == paramt_name) and (parameters.get("in") == path_type):
                            key = parameters.get("name")
                            value = parameters.get("type")
                            if param.get("required"):
                                required_bool = str(param.get("required"))
                            else:
                                required_bool = "-"
                            f.write('| ' + key + ' | ' + value + ' | ' + path_type + ' | ' + required_bool + " |" + "\n")
                            counter += 1

                if ('in' in param) and (param.get("in") == path_type):
                    key = param.get("name")
                    value = param.get("type")
                    if param.get("required"):
                        required_bool = str(param.get("required"))
                    else:
                        required_bool = "-"
                    f.write('| ' + key + ' | ' + value + ' | ' + path_type + ' | ' + required_bool + " |" + "\n")
                    counter += 1

    def get_path_types(self, api_content):
        path_types_list = []
        if "parameters" in api_content:
            parameters = api_content.get("parameters")

            for param in parameters:
                if "$ref" in param:
                    paramt_name = self.get_name_from_reference(param.get("$ref"))
                    for param_name, parameters in list(self.parser.parameters().items()):
                        if (param_name == paramt_name):
                            path_types_list.append(parameters.get("in"))

                if ('in' in param):
                    path_types_list.append(param.get("in"))
        return path_types_list

    def print_body_parameters(self, definitions, method_props, f):
        '''
        prints examples for requested schema in json
        :param definitions: definitions object
        :param method_props: properties of method object
        :param f: file object
        :return:
        '''
        if 'parameters' in method_props:
            parameters = method_props.get("parameters")
            for params in parameters:
                if '$ref' in params:
                    param = self.get_name_from_reference(params.get("$ref"))
                    for param_ref, param_ref_value in list(self.parser.parameters().items()):
                        param__name = param_ref_value.get("name")
                        if (param_ref == param) and (param_ref_value.get('in') == "body"):
                            f.write("**" + param__name + "**:" + "\n")
                            f.write("```json" + "\n\n")
                            swagger_sample = SwaggerSampleSchema(definitions, param_ref_value.get("schema"))
                            example_dict = swagger_sample.get_data_dict()
                            f.write(json.dumps(example_dict, indent=4) + "\n")
                            f.write("```" + "\n\n")

                if params.get("in") == "body":
                    param__name = params.get("name")
                    f.write("**" + param__name + "**:" + "\n")
                    f.write("```json" + "\n\n")
                    swagger_sample = SwaggerSampleSchema(definitions, params.get("schema"))
                    example_dict = swagger_sample.get_data_dict()
                    f.write(json.dumps(example_dict, indent=4) + "\n")
                    f.write("```" + "\n\n")

    def print_all_responses_res_schema(self, definitions, method_props, f):
        '''
        prints examples for success response schema in json
        :param definitions: definitions object
        :param method_props: properties of method object
        :param f: file object
        :return:
        '''

        responses_types = list(method_props.get("responses").keys())
        for each in responses_types:
            f.write("**" + each + "**:" + "\n")
            f.write("```json" + "\n\n")
            response = method_props.get("responses").get(each).get("schema")
            response1 = method_props.get("responses").get(each).get('$ref')
            description = method_props.get("responses").get(each).get('description')
            if response:
                swagger_sample = SwaggerSampleSchema(definitions, response)
                example_dict = swagger_sample.get_data_dict()
                f.write(json.dumps(example_dict, indent=4) + "\n")
            if response1:
                api_name = self.get_name_from_reference(response1)
                for res_name, res_ref in list(self.parser.responses().items()):
                    if (api_name == res_name):
                        swagger_sample = SwaggerSampleSchema(definitions, res_ref.get("schema"))
                        example_dict = swagger_sample.get_data_dict()
                        f.write(json.dumps(example_dict, indent=4) + "\n")
            f.write("```" + "\n\n")

    def get_security_scopes(self, api_content, security_dict, f):
        if api_content.get("security"):
            security = api_content.get("security")
            sec_type = list(security[0].keys())
            for each_sec_type in sec_type:
                sec_type_scopes = security[0].get(each_sec_type)
                if str(each_sec_type) == "oauth":
                    type = "oauth2"
                if str(each_sec_type) == "apiKey":
                    type = "string"
                f.write("| " + each_sec_type + " | " )

                for i in range(len(sec_type_scopes)):
                    f.write("%s" % sec_type_scopes[i])
                    if i != len(sec_type_scopes) - 1:
                        f.write(", ")

                f.write(" | " + type + " | " + "\n")


        else:
            sec_types = list(security_dict.keys())
            for each_sec_type in sec_types:
                each_sec_type_val = security_dict.get(each_sec_type)
                sec_type_scopes = each_sec_type_val.get("scopes")
                scopes_lst = list(sec_type_scopes.keys())
                type = ""
                if str(each_sec_type) == "oauth":
                    type = "oauth2"
                if str(each_sec_type) == "apiKey":
                    type = "string"

                f.write("| " + each_sec_type + " | " )

                for i in range(len(scopes_lst)):
                    f.write("%s" % scopes_lst[i])
                    if i != len(scopes_lst) -1:
                        f.write(", ")

                f.write(" | " + type + " | " + "\n")

        f.write("\n\n")

    def convert_to_html(self, filename):
        import markdown2
        import codecs

        f = codecs.open(filename, mode="r")
        text = f.read()

        html = markdown2.markdown(text)
        a,b = filename.split(".")
        html_name = a + ".html"
        output_file = codecs.open(html_name, "w",
                                  errors="xmlcharrefreplace"
                                  )
        output_file.write(html)
