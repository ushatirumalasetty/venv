

__author__ = 'tanmay.ibhubs'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    can_import_settings = True
    help = 'Does linting on all the project \n' \
           'Checks python files of given project and reviews them'

    @staticmethod
    def to_add_file(file_name, ignore_files, pattern):
        import re
        if not file_name.endswith(".py"):
            return False
        if file_name.startswith(tuple(ignore_files)):
            return False
        if pattern and re.match(pattern, file_name):
            return False
        return True

    def add_arguments(self, parser):
        parser.add_argument('-o', '--target', nargs='?', type=str,
                            help="Target package", required=False)
        parser.add_argument('-a', '--apps', nargs='*', type=str,
                            help="App Name from swagger_apps")
        parser.add_argument('-j', '--jobs', nargs='?', type=str,
                            help="")
        parser.add_argument('-E', '--errors-only', action='store_true',
                            help='Check only for error', required=False)
        parser.add_argument('-d', '--ignore-dirs',
                            nargs='*',
                            type=str,
                            help='Ignore directories',
                            required=False)
        parser.add_argument('-f', '--ignore-file-pattern',
                            type=str,
                            help='Ignore file pattern eg: r"(game_).*[.py]$"',
                            required=False)

    def handle(self, *args, **options):
        '''

        :param args: arguments given in the command
        :param options: options to the arguments ex app name
        :return:
        '''
        from django.conf import settings

        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        apps = options['apps']
        jobs = options['jobs']
        errors_only = options['errors_only']
        ignore_dirs_custom = options.get('ignore_dirs', None)
        ignore_file_pattern = options.get('ignore_file_pattern', None)

        # by default, it will run parallel processes based on cpu count
        if not jobs:
            jobs = '0'

        if not apps:
            apps = swagger_apps

        raise_exit = False
        for app in apps:
            print("Executing %s" % app)
            from colored import fg, attr
            if app not in swagger_apps:
                print('{}{}{}\'{}\' not found in swagger_apps. '
                      'Please add it first.'.format(
                        fg(1), attr(1), attr(4), app))
                print('App', app, ' not found in swagger_apps')
                raise_exit = True
            # get_concerned files
            ignore_files = ['snap_', 'request_response']
            ignore_dirs = ['api_spec', 'build', 'conf', 'interfaces',
                           'migrations', 'snapshots']

            if ignore_dirs_custom:
                ignore_dirs.extend(ignore_dirs_custom)

            import os
            path = os.path.join('./', app)
            py_files = []
            print("Ignoring Directories ==>", ignore_dirs_custom)
            print("Ignoring Files Matching Pattern ==>", ignore_file_pattern)
            for root, directories, files in os.walk(path):
                directories[:] = [d for d in directories if
                                  d not in ignore_dirs]
                for x in files:
                    if self.to_add_file(x, ignore_files, ignore_file_pattern):
                        py_files.append(os.path.join(root, x))
            if py_files:
                # files = 'Files to check => ' + ', '.join(py_files)
                # color_print(files, color='red', highlight='yellow',
                #             underline=True, bold=True)
                from pylint.lint import Run

                # disable_msg_ids will disable the checks
                # enable_msg_ids will enable only those lint checks
                # list of messages are at http://pylint-messages.wikidot.com/all-messages

                jobs_options = '--jobs=' + jobs
                args = [jobs_options]

                if errors_only:
                    args.append('--errors-only')

                args.extend(py_files)
                try:
                    Run(args)
                except SystemExit as exc:
                    if exc.code != 0:
                        print('Exception raised for app:', app)
                        raise_exit = True
            else:
                from colored import fg, attr
                print('{}{}{}\'{}\' doesn\'t has any python files.'
                      'Please add it first.'.format(
                      fg(1), attr(1), attr(4), app))
                continue

        if raise_exit:
            exit(1)

        return
