"""
Expects a class Fixture with method populate in app.utils.fixtures,
common.fixtures.app
"""


from importlib import import_module
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections


class Command(BaseCommand):
    can_import_settings = True
    help = 'Reloads data after completely flushing the database'
    requires_migrations_checks = True

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout=stdout, stderr=stderr,
                                      no_color=no_color)
        self.cursor = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to flush. Defaults to the "default" '
                 'database.',
        )

    def handle(self, *args, **options):
        """

        :param args: arguments given in the command
        :param options: options to the arguments ex app name
        :return:
        """
        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
        database = options['database']
        connection = connections[database]
        self.cursor = connection.cursor()
        verbosity = options["verbosity"]
        interactive = options["interactive"]
        if interactive:
            confirm = eval(input("""You have requested a data reload in the database.
This will IRREVERSIBLY DESTROY all data currently in the %r database,
and loads data from fixture scripts in app.utilities.fixtures.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """ % connection.settings_dict[
                'NAME']))
        else:
            confirm = 'yes'
        if confirm.lower() in ('y', 'yes'):
            tp_swagger_apps = settings.THIRD_PARTY_SWAGGER_APPS
            swagger_apps = list(django_swagger_utils_settings['APPS'].keys())
            from django.core.management import call_command
            self.stdout.write("Flushing data from {} ... ".format(
                connection.settings_dict['NAME']), ending="")
            self.stdout.flush()
            call_command('flush', interactive=False, database=database,
                         verbosity=verbosity)
            self.stdout.write(self.style.SUCCESS("OK"))
            for tp_app in tp_swagger_apps:
                try:
                    fixture = import_module('.{}_fixtures'.format(tp_app),
                                            'common.fixtures')
                    self.load_data(fixture, tp_app)
                except ImportError:
                    pass
            for app in swagger_apps:
                try:
                    fixture = import_module('.utils.fixtures', app)
                    self.load_data(fixture, app)
                except ImportError:
                    pass
        else:
            self.stdout.write("Data reload cancelled.\n")

    def load_data(self, fixture, app):
        if hasattr(fixture, 'Fixture') and hasattr(fixture.Fixture,
                                                   'populate'):
            self.stdout.write(
                "Loading data for {} ... ".format(app))
            self.stdout.flush()
            fixture.Fixture.populate()
            self.stdout.write(self.style.SUCCESS("OK"))
