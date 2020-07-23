# coding=utf-8
from django_swagger_utils.drf_server.exceptions.custom_exception import CustomException


class UserNotFoundException(CustomException):
    pass
