import os
import re
import shutil

from django.template import Template, Context

from django_swagger_utils.core.utils.case_convertion import to_camel_case
from django_swagger_utils.core.utils.write_to_file import write_to_file
from io import open


class SetupPyGenerator(object):
    def __init__(self, app_name, paths):
        self.app_name = app_name
        self.paths = paths

    def setup_template(self):
        context_dict = {
            'app_name_capital': to_camel_case(self.app_name.capitalize()),
            'app_name_upper': self.app_name.upper(),
            'app_name': self.app_name,
            'author': 'iB'
        }
        from django_swagger_utils.api_client.templates \
            .setup_py import setup_template
        template = Template(setup_template)
        data = template.render(Context(context_dict))
        write_to_file(data, self.paths['client_setup_py_path'])

    @staticmethod
    def update_version(*file_paths):
        filename = os.path.join(os.path.dirname(__file__), *file_paths)
        version_file = open(filename).read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  version_file, re.M)
        if version_match:
            return version_match.group(1)
        else:
            version_file = open(filename, "a")
            version_file.write("__version__ = '0.0.1'")
            version_file.write('\n')
            return "0.0.1"

    def generate_init_file(self):
        self.update_version(self.paths["app_base_path"], '__init__.py')
        shutil.copy(self.paths["base_app_init_file"],
                    self.paths["client_app_init_file"])
