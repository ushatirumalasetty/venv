from django_swagger_utils.drf_server.exceptions.custom_exception import CustomException


class BadRequest(CustomException):
    pass
