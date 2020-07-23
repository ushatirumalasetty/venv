
from django.core.management import ManagementUtility
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    can_import_settings = True
    help = 'Run Tests for basic of swagger util apps'

    def add_arguments(self, parser):
        parser.add_argument('-b', '--basic', action='store_true',
                            help='Run Basic Tests')
        parser.add_argument('--keepdb', action='store_true', help='Keep DB')
        parser.add_argument('--parallel', type=int, help='concurrency',
                            default=1)
        parser.add_argument('app', nargs='*', type=str, help="list of apps")

    def handle(self, *args, **options):
        """

        :param args: arguments given in the command
        :param options: options to the arguments ex app name
        :return:
        """
        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        try:
            from django_swagger_utils.drf_server.utils.server_gen. \
                get_api_environment import check_to_execute_mock_tests_for_apps
            apps = options['app']
            concurrency_count = options.get('parallel', 1)
            if not apps:
                apps = swagger_apps
            base_dir = settings.BASE_DIR
            for app_name in apps:

                if check_to_execute_mock_tests_for_apps(app_name):
                    from colored import fg, attr
                    print("{}{}{}Running Tests on app: {}".format(
                        fg(2), attr(1), attr(2), app_name))
                    from django_swagger_utils.drf_server.utils.server_gen. \
                        get_app_test_labels import get_app_test_labels
                    app_test_labels = get_app_test_labels(base_dir=base_dir,
                                                          app_name=app_name)
                    cmd = ["", "test"]
                    if options.get('keepdb'):
                        cmd.append('--keepdb')
                    if concurrency_count > 1:
                        cmd.append('--parallel='+str(concurrency_count))
                    cmd.extend(app_test_labels)

                    print("{}{}{}python manage.py ".format(
                        fg(4), attr(1), attr(4)).join(cmd))
                    print("\n")

                    utility = ManagementUtility(cmd)
                    try:
                        utility.execute()
                    except AttributeError as err:
                        print(err)
                        self.stderr.write("You should build APIs first.")
                        raise
                else:
                    pass
        except Exception as err:
            self.stderr.write(str(err))
            print(err)
            exit(1)
            raise
