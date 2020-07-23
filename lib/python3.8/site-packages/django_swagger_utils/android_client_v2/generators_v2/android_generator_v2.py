# from django_swagger_utils.android_client_v2.generators_v2.android_model_generator_v2 import AndroidModelGeneratorV2
import collections
from django.template import Template, Context

from django_swagger_utils.android_client_v2.constants import J2_APP_NAME_PREFIX
from django_swagger_utils.core.generators.generator import Generator


class AndroidGeneratorV2(Generator):
    def __init__(self, app_name, parser, paths, base_path):
        Generator.__init__(self, app_name, parser, paths, base_path)
        self.parser = parser
        self.paths = paths
        self.base_path = base_path

    def convert_data_types_to_java_format_v2(self, model_parameters):
        """
        to convert data types of open api of open api format to java format
        :param model_parameters:
        :return:
        """
        for mp in model_parameters:
            value = model_parameters[mp]

            model_parameters[mp] = self.get_corresponding_java_data_type_v2(value)

        return model_parameters

    def get_import_statement_from_path_v2(self, path):
        """
        to replace '/' by '.' in the path so that we obtain a statement according to java syntax
        :param path:
        :return: import statement in java format
        """
        import re
        k = re.split("/build/", path)
        if len(k) > 1:
            return k[1].replace("/", ".")
        else:
            return ""

    def generate_nested_models_v2(self, model_parameters, base_path=None):
        """
        to generate models for definations where we have nested definations
        :param model_parameters:
        :param base_path:
        :return:
        """
        if base_path is None:
            base_path = self.base_path
        for mp in model_parameters:
            mp_type = type(model_parameters[mp][0])
            if mp_type is dict:
                import os
                if not os.path.exists(self.paths["android_base_dir"] + "/models/common/" + self.snake_to_camel_case(
                    self.remove_array_notation_from_name(mp)) + ".java"):
                    # from django_swagger_utils.android_client_v2.generators_v2.android_model_generator import AndroidModelGenerator
                    android_model_generator = AndroidModelGeneratorV2(self.app_name, self.parser, self.paths, mp,
                                                                      base_path,
                                                                      model_parameters[mp][0])
                    android_model_generator.generate_android_model_v2()
                param_desc = model_parameters[mp][1]
                param_req = model_parameters[mp][2]
                model_parameters.pop(mp, None)
                model_parameters[self.remove_array_notation_from_name(mp)] = (
                    self.snake_to_camel_case(mp), param_desc, param_req)
        return model_parameters

    @staticmethod
    def get_corresponding_java_data_type_v2(data_type):
        """
       this will output datatypes in java format
       for example the parameter is or type number in spec file
       it is now converted into Double as Number is not supported in java and
       Double is a primitive datatype
       same applies to integer into Integer or int and string into String
       in case of nested definations the inner defination is returned
       Note: as a seperate class is created for each defination and a class is user defined
       datatype in java
       :param data_type:
       :return:
       """
        if 'Integer' == data_type:
            return data_type.replace('Integer', 'Integer')
        elif 'Number' == data_type:
            return data_type.replace('Number', 'Double')
        elif 'String' == data_type:
            return data_type.replace('String', "String")
        elif 'Boolean' == data_type:
            return data_type.replace('Boolean', "Boolean")
        elif 'integer' == data_type:
            return data_type.replace('integer', 'Integer')
        elif 'number' == data_type:
            return data_type.replace('number', 'Double')
        elif 'string' == data_type:
            return data_type.replace('string', "String")
        elif 'boolean' == data_type:
            return data_type.replace('boolean', "Boolean")
        elif 'string[]' == data_type:
            return data_type.replace('string', "String")
        elif "integer[]" == data_type:
            return data_type.replace("integer[]", "Integer[]")
        else:
            return data_type

    def generate_all_models_v2(self):
        """
       generates models from definations

       the logic is written in method generate_android_model() in android_model_generator.py
       :return:
       """
        for def_name, definition in list(self.parser.definitions().items()):
            # from django_swagger_utils.android_client_v2.generators_v2.android_model_generator_v2 import \
            # AndroidModelGeneratorV2
            android_model_generator = AndroidModelGeneratorV2(self.app_name, self.parser, self.paths, def_name,
                                                              self.base_path + "/models/common")

            android_model_generator.generate_android_model_v2()

    def generate_android_requests_responses_v2(self):
        """
       #generates request response files
       the logic is written in method generate_android_request_response() in android_request_response_generator.py
       return:
      """
        for path_name, path in list(self.parser.paths().items()):
            for method, method_props in list(path.items()):
                if (method == "post") or (method == "get") or (method == "put") or (method == "delete"):
                    base_path = self.paths["android_base_dir"]

                    from django_swagger_utils.android_client_v2.generators_v2.android_request_response_generator_v2 import \
                        AndroidRequestResponseGeneratorV2

                    android_request_generator = AndroidRequestResponseGeneratorV2(self.app_name, self.parser, path,
                                                                                  method_props,
                                                                                  self.paths,
                                                                                  base_path)
                    android_request_generator.generate_android_request_response_v2()

    def generate_android_server_commands_v2(self):
        """
       generates server commands interface file
       the logic is written in method generate_android_server_commands() in android_server_commands_generator.py

       :return:
       """
        base_path = self.paths["android_base_dir"]

        from django_swagger_utils.android_client_v2.generators_v2.android_server_commands_v2 import \
            AndroidServerCommandsGeneratorV2
        android_server_commands_generator = AndroidServerCommandsGeneratorV2(self.app_name, self.parser, self.paths,
                                                                             base_path)
        android_server_commands_generator.generate_android_server_commands_v2()

    def check_if_request_is_array_v2(self, req_parameters):
        """

       :param req_parameters:
       :return:
       """
        if len(req_parameters) != 1:
            return False
        else:
            for rp in req_parameters:
                param_type = req_parameters[rp][0]
                if self.is_array(param_type):
                    return True
                elif self.is_array(rp):
                    return True
                else:
                    return False

    def check_if_response_is_array_v2(self, method_props):
        """

       :param method_props:
       :return:
       """
        if 'responses' in method_props:
            response = ''
            schema = ''
            if '200' in method_props.get("responses"):
                response = method_props.get("responses").get("200")
            elif 'default' in method_props.get("responses"):
                response = method_props.get("responses").get("default")

            if 'schema' in response:
                schema = response.get("schema")
            elif '$ref' in response:
                res_name = self.get_name_from_reference(response.get("$ref"))
                if 'schema' in self.parser.responses().get(res_name):
                    schema = self.parser.responses().get(res_name)
                    if self.parser.responses().get(res_name).get("schema").get("type") == "array":
                        return True

            if ('type' in schema) and (schema.get("type") == "array"):
                return True
            return False

    def regenerate_model_if_array_v2(self, parameters):
        """
       regenerates model if defination is of type array
       :param parameters:
       :return:
       """
        for param in parameters:
            param_type = parameters[param][0]
            # print "checking if array and definition: " + param
            if self.is_array(param_type) and self.is_definition(param_type):
                android_model_generator = AndroidModelGeneratorV2(self.app_name, self.parser, self.paths,
                                                                  self.remove_array_notation_from_name(param_type),
                                                                  self.base_path + "/models/common",
                                                                  is_used_as_list=True)
                android_model_generator.generate_android_model_v2()

    def check_if_parameters_are_optional_v2(self, parameters):
        """
      #checks if parameters are optional ormandatory
      :param parameters:
      :return:
      """
        for param in parameters:
            if parameters[param][2] is False:
                return True
        return False

    def generate_jars_v2(self, vnum):
        """
        to generate .class file and copy them in build folder to target folder
        :return:
        """
        import os
        import shutil

        from cookiecutter.main import cookiecutter
        version = "0.0.%d" % vnum
        template_dir = os.getcwd() + "/maven_repo_%s" % self.app_name
        os.environ.update({"OLDPWD": os.getcwd()})
        if os.path.exists(template_dir):
            shutil.rmtree(template_dir)
        clone_url = "git@bitbucket.org:rahulsccl/maven_repo_template.git"
        template_dir = cookiecutter(clone_url,
                                    extra_context={'version': version, 'app_name': self.app_name + J2_APP_NAME_PREFIX},
                                    overwrite_if_exists=True, no_input=True, checkout="v2")
        to_path = template_dir + "/src/main/java"
        from_path = self.paths["android_base_dir"]

        def copy_and_overwrite_v2(from_path, to_path):
            if os.path.exists(to_path):
                shutil.rmtree(to_path)
            shutil.copytree(from_path, to_path)

        copy_and_overwrite_v2(from_path, to_path)
        # shutil.rmtree(template_dir)

        # from django_swagger_utils.android_client_v2.generators_v2.android_generator_v2 import AndroidGeneratorV2


class AndroidModelGeneratorV2(AndroidGeneratorV2):
    def __init__(self, app_name, parser, paths, model_name, base_path, model_parameters=None,
                 is_used_as_list=False):
        AndroidGeneratorV2.__init__(self, app_name, parser, paths, base_path)
        self.model_name = self.snake_to_camel_case(self.remove_array_notation_from_name(model_name))
        self.model_parameters = model_parameters
        self.is_used_as_list = is_used_as_list

    def generate_android_model_v2(self):
        """
        generates model for the provided definations
        this creates a class with class variables obtained from properties in spec file
        , class constructors and  methods
        if properties are not mentioned as required , constructors are created with and without parameters
        :return:
        """
        if self.model_parameters is None:
            self.model_parameters = self.get_definition_parameters(self.model_name)
            # self.model_parameters = self.get_type_dict_only(self.model_parameters)
        self.model_parameters = self.generate_nested_models_v2(self.model_parameters)
        self.has_optional_parameters = self.check_if_parameters_are_optional_v2(self.model_parameters)
        self.model_parameters = self.get_type_dict_only(self.model_parameters)
        # self.model_parameters = sorted(self.model_parameters.items())
        self.model_parameters = collections.OrderedDict(sorted(self.model_parameters.items()))

        android_model_file_content = self.android_model_file_contents_v2()
        self.write_android_model_file_v2(android_model_file_content)

    def android_model_file_contents_v2(self):
        """
       here we create a dictionary with all the elements required for a model java source file
       and then generate according to template of java syntaxes
       the template is present in android_model.py in templates folder
       :return:
       """
        self.model_parameters = self.convert_data_types_to_java_format_v2(self.model_parameters)
        android_model_context = {
            "android_app_name": self.app_name,
            "android_import_statement": self.get_import_statement_from_path_v2(self.base_path),
            "model_parameters": list(self.model_parameters.items()),
            "android_model_camel_case_name": self.model_name,
            "android_model_is_used_as_list": self.is_used_as_list,
            "android_model_has_optional_parameters": self.has_optional_parameters
        }

        from django_swagger_utils.android_client_v2.templates_v2.android_model import ANDROID_MODEL
        android_model_template = Template(ANDROID_MODEL)
        context = Context(android_model_context)
        return android_model_template.render(context)

    def write_android_model_file_v2(self, android_model_file_content):
        """
        the generated model template in above method is saved with .java extension
        and saved in models folder
        :param android_model_file_content:
        :return:
        """
        android_model_file_path = self.base_path + "/" + self.model_name + ".java"
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(android_model_file_content, android_model_file_path, False)

        # os.system("mvn deploy -s settings.xml")
        # jar_path = template_dir + "/target/%s-%s.jar" % (self.app_name, version)
        # print jar_path
        # os.chdir(os.environ["OLDPWD"])
        #
        # if not os.path.exists(self.paths["global_jars_dir"]):
        #     os.mkdir(self.paths["global_jars_dir"])
        # shutil.copy2(jar_path, self.paths["global_jars_dir"])
        # shutil.rmtree(template_dir)
