fixture_template = """{% autoescape off %}__author__ = 'ibhubs'


class Fixture(object):
    \"\"\"
    Class contains populate method as static method
    Is used by django-swagger-utils as a management command
    \"\"\"

    @staticmethod
    def populate():
        \"\"\"
        Populates data for app {{app_name}}
        :return:
        \"\"\"
        pass
{% endautoescape %}"""
