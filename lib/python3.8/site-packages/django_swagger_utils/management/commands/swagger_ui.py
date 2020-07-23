

import os

from django.core.management.base import BaseCommand
from io import open


class Command(BaseCommand):
    can_import_settings = True
    help = 'Generate swagger UI Dist for given apps'

    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*', type=str, help="list of apps")

    @staticmethod
    def write_index_html(ref_html_path, dest_html_path, swagger_spec_path):

        from django.template import Template, Context
        html_file = open(ref_html_path)
        html = html_file.read()
        html_file.close()

        serializer_template = Template(html)
        spec_file = open(swagger_spec_path)
        specs = spec_file.read()

        context = Context({"spec_json": specs})

        html_file_w = open(dest_html_path, "w")
        html_file_w.write(serializer_template.render(context))
        html_file_w.close()

    def handle(self, *args, **options):
        """

        :param args: arguments given in the command
        :param options: options to the arguments ex app name
        :return:
        """

        # todo host and enabling testing in swagger spec
        # todo third party and lib apps support

        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        try:
            from django_swagger_utils.drf_server.utils.server_gen. \
                get_api_environment import check_to_execute_mock_tests_for_apps
            apps = options['app']
            if not apps:
                apps = swagger_apps
            base_dir = settings.BASE_DIR

            replace_str = "management/commands/swagger_ui.py"
            if __file__.endswith("c"):
                replace_str += "c"
            dsu_base_path = __file__.replace(replace_str, "")
            dist_path = os.path.join(dsu_base_path, "templates", "swagger_ui")

            swagger_ui_base_dir = os.path.join(base_dir, "swagger_ui")
            try:
                os.mkdir(swagger_ui_base_dir)
            except OSError:
                pass

            for app_name in apps:
                app_ui_dist = os.path.join(swagger_ui_base_dir, app_name)
                from django_swagger_utils.utils.file_utils import \
                    copy_directory, rm_directory
                rm_directory(app_ui_dist)
                copy_directory(dist_path, app_ui_dist)

                ref_html_path = os.path.join(dist_path, "index.html")
                dest_html_path = os.path.join(app_ui_dist, "index.html")
                swagger_spec_path = os.path.join(base_dir, app_name,
                                                 "api_specs", "api_spec.json")

                self.write_index_html(ref_html_path, dest_html_path,
                                      swagger_spec_path)
                print("%s: Done" % app_name)
        except Exception as err:
            self.stderr.write(str(err))
            print(err)
            exit(1)
