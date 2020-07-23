interface_template = """{% autoescape off %}from ib_common.interface_utils.interface_utils import InterfaceUtils
from django_swagger_utils.drf_server.utils.decorator.interface_decorator import interface_decorator
__author__ = '{{author}}'


class {{app_name_capital}}ServiceInterface(InterfaceUtils):

    def __init__(self, *args, **kwargs):
        super({{app_name_capital}}ServiceInterface, self).__init__(*args, **kwargs)

    @property
    def service_flag(self):
        from django.conf import settings
        from ib_common.constants.service_types import ServiceTypesEnum
        return getattr(settings, '{{app_name_upper}}_REQUEST_TYPE', ServiceTypesEnum.LIBRARY.value)

    @property
    def service_base_url(self):
        from django.conf import settings
        return self.clean_base_url(getattr(settings, '{{app_name_upper}}_BASE_URL', '')) + 'api/{{app_name}}'

    @property
    def client_key_details_id(self):
        return 1

    @staticmethod
    def service_source():
        from django.conf import settings
        return getattr(settings, '{{app_name_upper}}_SOURCE', '')

    @classmethod
    def conn(cls, user, access_token):
        return cls(user, access_token, cls.service_source())
    {% for method_name,http_method,url_tail in functions %}
    @interface_decorator('{{app_name}}','{{http_method}}','{{url_tail}}','{{method_name}}')
    def {{method_name}}(self, *args, **kwargs):
        pass
{% endfor %}{% endautoescape %}"""
