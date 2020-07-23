app_template = """{% autoescape off %}from django.apps import AppConfig


class {{camel_case_app_name}}AppConfig(AppConfig):
    name = "{{app_name}}"

    def ready(self):
        from {{app_name}} import signals # pylint: disable=unused-variable
{% endautoescape %}"""
