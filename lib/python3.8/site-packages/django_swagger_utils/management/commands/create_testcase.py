from django_swagger_utils.management.commands.build import Build

__author__ = 'tanmay.ibhubs'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    can_import_settings = True
    help = 'Create test case for a operation \n' \
           'Requires operation id and testcase number as arguments'

    def add_arguments(self, parser):
        parser.add_argument('-o', '--operation', nargs='?', type=str, help="OperationID from views package", required=True)
        parser.add_argument('-n', '--number', nargs='?', type=str, help="Test Case Number i.e. 01", required=True)
        parser.add_argument('-a', '--app', nargs='?', type=str, help="App Name from swagger_apps", required=True)

    def handle(self, *args, **options):
        '''

        :param args: arguments given in the command
        :param options: options to the arguments ex app name
        :return:
        '''
        from django.conf import settings
        base_dir = settings.BASE_DIR

        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        app = options['app']
        if app not in swagger_apps:
            from colored import fg, attr
            print('{}{}{}\'{}\' not found in swagger_apps. '
                  'Please add it first.'.format(fg(1), attr(1), attr(4), app))
            return
        # calling the concerned build methods for each app

        build = Build(app, base_dir, django_swagger_utils_settings)
        build.swagger_generator.generate_test_case(options['operation'], options['number'])

        return
