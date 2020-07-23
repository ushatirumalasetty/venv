import logging

from django.http import HttpResponse
from rest_framework.views import exception_handler

LOGGER = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    from rest_framework import exceptions
    exc_status_code = getattr(exc, 'status_code', 0)
    if isinstance(exc, exceptions.APIException) and exc_status_code == 500:
        LOGGER.error(exc)

    # Now add the HTTP status code to the response.
    if response is not None:
        if isinstance(response, HttpResponse):
            return response
        details = response.data.get("detail", None)
        if details:
            details = str(details)
        else:
            import json
            details = json.dumps(response.data)
        custom_data = {
            "status": "NOT_OK",
            "message": "BadRequest",
            "errors": [
                {
                    "code": response.status_code,
                    "description": details,
                    "message": "could not satisfy the request"
                }
            ]
        }
        response.data = custom_data

    return response
