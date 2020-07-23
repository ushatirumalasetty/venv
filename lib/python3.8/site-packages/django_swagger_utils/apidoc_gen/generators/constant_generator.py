from io import open
class ConstantGenerator(object):

    def __init__(self, parser):
        self.parser = parser

    def constant_gen(self, filename):
        f = open(filename, "w")
        f.write("from enum import Enum\n")
        f.write("from ib_common.constants.base_enum_class import BaseEnumClass\n")
        f.write("\n\n")

        f.close()
        class_name_lst = []

        definitions = self.parser.definitions()
        parameters = self.parser.parameters()
        paths = self.parser.paths()
        responses = self.parser.responses()

        dicts_list = [definitions, parameters, paths, responses]
        for each_dict in dicts_list:
            if each_dict == paths:
                for path, api in list(each_dict.items()):
                    for api_method, api_content in list(api.items()):
                        if (api_method == 'get') or (api_method == 'post') or (api_method == 'delete') or (
                            api_method == 'put'):
                            if api_content.get("parameters"):
                                parameters_lst = api_content.get("parameters")
                                for each in parameters_lst:
                                    if each.get("schema"):
                                        schema_value = each.get("schema")
                                        dictionary = schema_value
                                        self.file_write(filename, dictionary, class_name_lst)
                            if api_content.get("responses"):
                                responses_value = api_content.get("responses")
                                if responses_value.get("200"):
                                    value_200 = responses_value.get("200")
                                    if value_200.get("schema"):
                                        schema_value = value_200.get("schema")
                                        dictionary = schema_value
                                        self.file_write(filename, dictionary, class_name_lst)
                        if api_method == 'parameters':
                            for each in api_content:
                                if each.get("schema"):
                                    schema_value = each.get("schema")
                                    dictionary = schema_value
                                    self.file_write(filename, dictionary, class_name_lst)

            if each_dict == parameters or each_dict == responses:
                for key, value in list(each_dict.items()):
                    if value.get("schema"):
                        schema_value = value.get("schema")
                        dictionary = schema_value

                        self.file_write(filename, dictionary, class_name_lst)

            if each_dict == definitions:
                for key,value in list(each_dict.items()):
                    if value.get("properties"):
                        dictionary = value
                        self.file_write(filename, dictionary, class_name_lst)

    def file_write(self, filename, dictionary, class_name_lst):
        f = open(filename, "a")

        if dictionary.get("items"):
            items_value = dictionary.get("items")
            if items_value.get("properties"):
                self.file_write(filename, items_value, class_name_lst)

        if dictionary.get("properties"):
            properties_value = dictionary.get("properties")

            for each_key, each_value in list(properties_value.items()):
                if "items" in list(each_value.keys()):
                    items_values = each_value.get("items")
                    if items_values.get("properties"):
                        self.file_write(filename, items_values, class_name_lst)
                if "enum" in list(each_value.keys()):
                    enm_value = each_value.get("enum")
                    class_name = ""
                    each_key_parts = each_key.split("_")
                    for each in each_key_parts:
                        each = each.title()
                        class_name = class_name + each

                    if class_name not in class_name_lst:
                        class_name_lst.append(class_name)
                        f.write("class" + " " + class_name + "(BaseEnumClass, Enum):" + "\n")
                        for each in enm_value:
                            f.write("\t" + each + " = " + '"' + each + '"' + "\n")
                        f.write("\n\n")
        f.close()
