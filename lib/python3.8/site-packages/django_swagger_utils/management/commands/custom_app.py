

import os

from django.core.management.base import BaseCommand


class CreateCustomApp(object):
    def __init__(self, app_name, base_path, project_name):
        self.app_name = app_name
        self.base_path = base_path
        self.camel_case_app_name = ''.join(
            x.capitalize() or '_' for x in app_name.split('_'))
        self.project_name = project_name
        self.upper_case_project_name = project_name.upper()

    def create_app_py(self):
        from django_swagger_utils.core.utils.write_to_file import \
            write_to_file
        app_py_file_path = os.path.join(self.base_path, self.app_name, "app.py")
        from django_swagger_utils.utils.custom_app_templates.app_template import \
            app_template
        from django.template.base import Template
        from django.template.context import Context
        app_template_init = Template(app_template)
        app_template_content = app_template_init.render(Context({
            'camel_case_app_name': self.camel_case_app_name,
            'app_name': self.app_name
        }))
        write_to_file(app_template_content, app_py_file_path)

    def get_service_adapter_content(self):
        from django_swagger_utils.utils.custom_app_templates.service_adapter_template import \
            service_adapter_template
        from django.template.base import Template
        from django.template.context import Context
        service_adapter_init = Template(service_adapter_template)
        service_adapter_content = service_adapter_init.render(Context({
            'upper_case_project_name': self.upper_case_project_name,
            'app_name': self.app_name
        }))
        return service_adapter_content

    def create_init_py(self):
        from django_swagger_utils.drf_server.utils.server_gen.get_api_environment import \
            check_to_execute_mock_tests_for_apps
        from django_swagger_utils.core.utils.write_to_file import \
            write_to_file

        view_file_init_file_path = os.path.join(self.base_path, self.app_name, "__init__.py")
        view_init_file_contents = "default_app_config = \"" + self.app_name + ".app." + self.camel_case_app_name + "AppConfig\" # pylint:disable=invalid-name\n"  # pylint: disable=invalid-name"
        view_init_file_contents += "\nEXECUTE_API_TEST_CASE = " + str(
            check_to_execute_mock_tests_for_apps(self.app_name))
        view_init_file_contents += "\n__version__ = '0.0.1'\n"
        write_to_file(view_init_file_contents, view_file_init_file_path)

    def update_model_init_file(self):
        from django_swagger_utils.core.utils.write_to_file import \
            write_to_file
        model_init_path = os.path.join(self.base_path, self.app_name, "models", "__init__.py")
        model_init_content = self.get_model_init_content()
        write_to_file(model_init_content, model_init_path)

    def get_fixture_file_content(self):
        from django_swagger_utils.utils.custom_app_templates.fixture_template import \
            fixture_template
        from django.template.base import Template
        from django.template.context import Context
        fixture_file_init = Template(fixture_template)
        fixture_file_content = fixture_file_init.render(Context({
            'app_name': self.app_name
        }))
        return fixture_file_content

    def create_app(self):
        """
        creates new app
        :return:
        """
        app_base_path = os.path.join(self.base_path, self.app_name)
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists
        # if app is present already
        if check_path_exists(app_base_path):
            print("'{0:s}' already exists".format(self.app_name))
            exit()
        else:
            # write all default file
            folders_list, files_list = self.get_default_files_list()
            for each_file in list(files_list.values()):
                from django_swagger_utils.core.utils.write_to_file import \
                    write_to_file
                write_to_file(each_file[1], each_file[0])

            self.create_app_py()
            self.create_init_py()

            for each_folder in list(folders_list.values()):
                from django_swagger_utils.core.utils.mk_dirs import MkDirs
                MkDirs().mk_dir_if_not_exits(file_name=each_folder)
            self.update_model_init_file()
        print("'{0:s}' created".format(self.app_name))
        os.system("tree {0:s}".format(self.app_name))

        # todo: updated swagger_utils settings.apps

    def get_default_files_list(self):
        # creates path for default files and returns folders and files dict
        app_base_path = os.path.join(self.base_path, self.app_name)
        api_specs_dir = os.path.join(app_base_path, 'api_specs')
        conf_dir = os.path.join(app_base_path, 'conf')
        adapters_dir = os.path.join(app_base_path, "adapters")
        utils_dir = os.path.join(app_base_path, "utils")
        signals_dir = os.path.join(app_base_path, "signals")

        sample_api_specs_json = self.get_sample_api_specs_json()
        service_adapter_content = self.get_service_adapter_content()
        fixture_file_content = self.get_fixture_file_content()
        files_list = {
            "api_spec_json": (
                os.path.join(api_specs_dir, 'api_spec.json'),
                sample_api_specs_json),
            "settings_file": (os.path.join(conf_dir, 'settings.py'),
                              "# write your %s settings" % self.app_name),
            "admin_py": (
                os.path.join(app_base_path, 'admin.py'),
                '# your django admin\n'),
            "service_adapter_file": (
                os.path.join(adapters_dir, 'service_adapter.py'),
                service_adapter_content),
            "fixture_file": (
                os.path.join(utils_dir, 'fixture.py'), fixture_file_content),
            "signals_py": (os.path.join(signals_dir, 'signals.py'), '')
        }

        folders_list = {
            "constants_dir": os.path.join(app_base_path, "constants/"),
            "models_dir": os.path.join(app_base_path, "models/"),
            "validators_dir": os.path.join(app_base_path, "validators/")
        }

        return folders_list, files_list

    def get_sample_api_specs_json(self):
        """
        returns a sample spec
        :return:
        """
        from django_swagger_utils.drf_server.utils.server_gen.sample_spec_file import \
            sample_spec_file
        sample_specs_json = sample_spec_file(self.app_name)
        return sample_specs_json

    @staticmethod
    def get_model_init_content():
        from django_swagger_utils.utils.custom_app_templates.model_init_template import \
            model_init_template
        from django.template.base import Template
        from django.template.context import Context
        model_init = Template(model_init_template)
        model_init_content = model_init.render(Context({}))
        return model_init_content


class Command(BaseCommand):
    can_import_settings = True
    help = 'Generate a custom swagger util template app'

    def add_arguments(self, parser):
        """
        retrieve each argument seperated by white space where each of them represent an app
        nargs=* indicates atleast 1 argument to be present
        to know more about arguments and nargs read the python documentaion
        :param parser:
        :return:
        """
        parser.add_argument('app', nargs='*', type=str, help="list of apps")
        parser.add_argument('-p', '--project', type=str, help="project_name",
                            required=True)

    def handle(self, *args, **options):
        from django.conf import settings
        base_dir = settings.BASE_DIR
        try:
            apps = options['app']
            project = options['project']
            if project not in base_dir:
                print('**** ERROR: Project name is not right ****')
                exit()
            if not apps:
                print("usage: python manage.py custom_app <app_names> ")
                exit()
            for app_name in apps:
                create_custom_app = CreateCustomApp(app_name, base_dir,
                                                    project)
                create_custom_app.create_app()
        except Exception as err:
            print(err)
            exit(1)
