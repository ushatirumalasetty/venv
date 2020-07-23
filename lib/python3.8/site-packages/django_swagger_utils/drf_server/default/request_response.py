from django.conf import settings

from django_swagger_utils.drf_server.default.parser_mapping import PARSER_MAPPING
from django_swagger_utils.drf_server.default.renderer_mapping import RENDERER_MAPPING

django_swagger_utils_settings = settings.SWAGGER_UTILS
defaults = django_swagger_utils_settings["DEFAULTS"]

REQUEST_RESPONSE_DECORATOR = {
    'METHOD': 'POST',
    'REQUEST_WRAPPING_REQUIRED': defaults.get("REQUEST_WRAPPING_REQUIRED", True),
    'REQUEST_ENCRYPTION_REQUIRED': defaults.get("REQUEST_ENCRYPTION_REQUIRED", False),
    'REQUEST_IS_PARTIAL': False,
    'REQUEST_SERIALIZER_MANY_ITEMS': False,
    'RESPONSE_SERIALIZER_MANY_ITEMS': False,
    'PARSER_CLASSES': [
        PARSER_MAPPING["application/json"],
    ],
    'RENDERER_CLASSES': [
        RENDERER_MAPPING["application/json"],
    ],
    "SECURITY": {
    },
    'REQUEST_SERIALIZER': None,
    'RESPONSE': {
        '200': {
            'CONTENT_TYPE': "application/json",
            'RESPONSE_SERIALIZER': None,
            'HEADERS_SERIALIZER': None,
        }
    }

}

SECURITY_DEFINITIONS = {

}
