# coding=utf-8

import logging

logger = logging.getLogger('dsu.debug')


def wrap_exceptions():
    """

    :return:
    """

    def decorator(function):

        """

        :param function:
        :return:
        """

        def handler(*args, **kwargs):
            from django.http import HttpResponse
            from rest_framework import status
            from django_swagger_utils.drf_server.utils.decorator.handle_custom_exceptions import \
                handle_custom_exceptions
            from django_swagger_utils.drf_server.exceptions.validation_error import ValidationError
            from django_swagger_utils.drf_server.exceptions.authentication_error import AuthenticationError
            from django_swagger_utils.drf_server.exceptions.view_enviroment_not_defined_error import \
                ViewEnvironmentNotDefinedError
            from django_swagger_utils.drf_server.exceptions.user_not_found import UserNotFoundException
            from django_swagger_utils.drf_server.exceptions.client_key_error import ClientKeyError
            from django_swagger_utils.drf_server.exceptions.method_not_allowed import MethodNotAllowed
            from django_swagger_utils.drf_server.exceptions.response_not_definied import ResponseNotDefined
            try:
                function_return_value = function(*args, **kwargs)
                return function_return_value
            except ValidationError as err:
                return HttpResponse(content=str(err), status=status.HTTP_400_BAD_REQUEST)
            except ClientKeyError as err:
                return HttpResponse(content=str(err), status=status.HTTP_400_BAD_REQUEST)
            except UserNotFoundException as err:
                return HttpResponse(content=str(err), status=status.HTTP_404_NOT_FOUND)
            except AuthenticationError as err:
                return HttpResponse(content=str(err), status=status.HTTP_401_UNAUTHORIZED)
            except ViewEnvironmentNotDefinedError as err:
                return HttpResponse(content=str(err), status=status.HTTP_501_NOT_IMPLEMENTED)
            except ResponseNotDefined as err:
                return HttpResponse(content=str(err), status=status.HTTP_501_NOT_IMPLEMENTED)
            except MethodNotAllowed as err:
                return HttpResponse(content=str(err), status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception as err:
                return handle_custom_exceptions(err)

        handler.__doc__ = function.__doc__
        return handler

    return decorator
