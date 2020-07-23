import os

from django.core.serializers import json

from django_swagger_utils.core.generators.generator import Generator


class AndroidGenerator(Generator):
    def __init__(self, app_name, parser, paths, base_path):

        Generator.__init__(self, app_name, parser, paths, base_path)
        self.parser = parser
        self.paths = paths
        self.base_path = base_path

    def convert_data_types_to_java_format(self, model_parameters):
        """
        to convert data types of open api of open api format to java format
        :param model_parameters:
        :return:
        """

        for mp in model_parameters:
            value = model_parameters[mp]

            model_parameters[mp] = self.get_corresponding_java_data_type(value)

        return model_parameters

    def get_import_statement_from_path(self, path):
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

    def generate_nested_models(self, model_parameters, base_path=None):
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
                    from django_swagger_utils.android_client.generators.android_model_generator import \
                        AndroidModelGenerator
                    android_model_generator = AndroidModelGenerator(self.app_name, self.parser, self.paths, mp,
                                                                    base_path,
                                                                    model_parameters[mp][0])
                    android_model_generator.generate_android_model()
                param_desc = model_parameters[mp][1]
                param_req = model_parameters[mp][2]
                model_parameters.pop(mp, None)
                model_parameters[self.remove_array_notation_from_name(mp)] = (
                    self.snake_to_camel_case(mp), param_desc, param_req)
        return model_parameters

    @staticmethod
    def get_corresponding_java_data_type(data_type):
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
        elif 'string[]' == data_type:
            return data_type.replace('string', "String")
        elif "integer[]" == data_type:
            return data_type.replace("integer[]", "Integer[]")
        elif "number[]" == data_type:
            return data_type.replace("number[]", "Double[]")
        elif 'boolean' == data_type:
            return data_type.replace('boolean', "Boolean")
        else:
            return data_type

    def generate_all_models(self):
        """
        generates models from definations
        the logic is written in method generate_android_model() in android_model_generator.py
        :return:
        """

        for def_name, definition in list(self.parser.definitions().items()):
            from django_swagger_utils.android_client.generators.android_model_generator import AndroidModelGenerator
            android_model_generator = AndroidModelGenerator(self.app_name, self.parser, self.paths, def_name,
                                                            self.base_path + "/models/common")

            android_model_generator.generate_android_model()

    def generate_android_requests_responses(self):
        """
        #generates request response files
        the logic is written in method generate_android_request_response() in android_request_response_generator.py
        return:
       """
        for path_name, path in list(self.parser.paths().items()):
            for method, method_props in list(path.items()):
                if (method == "post") or (method == "get") or (method == "put") or (method == "delete"):
                    base_path = self.paths["android_base_dir"]
                    from django_swagger_utils.android_client.generators.android_request_response_generator import \
                        AndroidRequestResponseGenerator
                    android_request_generator = AndroidRequestResponseGenerator(self.app_name, self.parser, path,
                                                                                method_props,
                                                                                self.paths,
                                                                                base_path)
                    android_request_generator.generate_android_request_response()

    def generate_android_server_commands(self):
        """
        generates server commands interface file
        the logic is written in method generate_android_server_commands() in android_server_commands_generator.py

        :return:
        """
        base_path = self.paths["android_base_dir"]
        from django_swagger_utils.android_client.generators.android_server_commands_generator import \
            AndroidServerCommandsGenerator
        android_server_commands_generator = AndroidServerCommandsGenerator(self.app_name, self.parser, self.paths,
                                                                           base_path)
        android_server_commands_generator.generate_android_server_commands()

    def check_if_request_is_array(self, req_parameters):
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

    def check_if_response_is_array(self, method_props):
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

    def regenerate_model_if_array(self, parameters):
        """
        regenerates model if defination is of type array
        :param parameters:
        :return:
        """
        for param in parameters:
            param_type = parameters[param][0]
            if self.is_array(param_type) and self.is_definition(param_type):
                from django_swagger_utils.android_client.generators.android_model_generator import AndroidModelGenerator
                android_model_generator = AndroidModelGenerator(self.app_name, self.parser, self.paths,
                                                                self.remove_array_notation_from_name(param_type),
                                                                self.base_path + "/models/common", is_used_as_list=True)
                android_model_generator.generate_android_model()

    def check_if_parameters_are_optional(self, parameters):
        """
        #checks if parameters are optional ormandatory
        :param parameters:
        :return:
        """
        for param in parameters:
            if parameters[param][2] is False:
                return True
        return False

    def generate_jars(self, vnum):
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
        # clones into maven repo (default branch master)
        if os.path.exists(template_dir):
            shutil.rmtree(template_dir)
        clone_url = "git@bitbucket.org:rahulsccl/maven_repo_template.git"
        template_dir = cookiecutter(clone_url, extra_context={'version': version, 'app_name': self.app_name},
                                    overwrite_if_exists=True, no_input=True)
        to_path = template_dir + "/src/main/java"
        from_path = self.paths["android_base_dir"]

        def copy_and_overwrite(from_path, to_path):
            # overwrites files if existing already
            if os.path.exists(to_path):
                shutil.rmtree(to_path)
            shutil.copytree(from_path, to_path)

        copy_and_overwrite(from_path, to_path)
        # shutil.rmtree(template_dir)



        # os.system("mvn deploy -s settings.xml")
        # jar_path = template_dir + "/target/%s-%s.jar" % (self.app_name, version)
        # print jar_path
        # os.chdir(os.environ["OLDPWD"])
        #
        # if not os.path.exists(self.paths["global_jars_dir"]):
        #     os.mkdir(self.paths["global_jars_dir"])
        # shutil.copy2(jar_path, self.paths["global_jars_dir"])
        # shutil.rmtree(template_dir)
