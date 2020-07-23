import collections

from django.template import Template, Context

from django_swagger_utils.android_client.generators.android_generator import AndroidGenerator


class AndroidModelGenerator(AndroidGenerator):
    def __init__(self, app_name, parser, paths, model_name, base_path, model_parameters=None, is_used_as_list=False):
        AndroidGenerator.__init__(self, app_name, parser, paths, base_path)
        self.model_name = self.snake_to_camel_case(self.remove_array_notation_from_name(model_name))
        self.model_parameters = model_parameters
        self.is_used_as_list = is_used_as_list

    def generate_android_model(self):
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
        self.model_parameters = self.generate_nested_models(self.model_parameters)
        self.has_optional_parameters = self.check_if_parameters_are_optional(self.model_parameters)
        self.model_parameters = self.get_type_dict_only(self.model_parameters)
        # self.model_parameters = sorted(self.model_parameters.items())
        self.model_parameters = collections.OrderedDict(sorted(self.model_parameters.items()))

        android_model_file_content = self.android_model_file_contents()
        self.write_android_model_file(android_model_file_content)

    def android_model_file_contents(self):
        """
        here we create a dictionary with all the elements required for a model java source file
        and then generate accoridng to template of java syntaxes
        the template is present in android_model.py in templates folder
        :return:
        """
        self.model_parameters = self.convert_data_types_to_java_format(self.model_parameters)
        android_model_context = {
            "android_app_name": self.app_name,
            "android_import_statement": self.get_import_statement_from_path(self.base_path),
            "model_parameters": list(self.model_parameters.items()),
            "android_model_camel_case_name": self.model_name,
            "android_model_is_used_as_list": self.is_used_as_list,
            "android_model_has_optional_parameters": self.has_optional_parameters
        }

        from django_swagger_utils.android_client.templates.android_model import ANDROID_MODEL
        android_model_template = Template(ANDROID_MODEL)
        context = Context(android_model_context)
        return android_model_template.render(context)

    def write_android_model_file(self, android_model_file_content):
        """
        the generated model template in above method is saved with .java extension
        and saved in models folder
        :param android_model_file_content:
        :return:
        """
        android_model_file_path = self.base_path + "/" + self.model_name + ".java"
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(android_model_file_content, android_model_file_path, False)
