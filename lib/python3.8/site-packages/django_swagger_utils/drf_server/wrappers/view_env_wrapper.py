# coding=utf-8

import importlib
import logging

logger = logging.getLogger('dsu.debug')


def view_env_wrapper(app_name, endpoint_name, group_name, *args, **kwargs):
    """

    :param app_name:
    :param endpoint_name:
    :param args:
    :param kwargs:
    :return:
    """

    from django_swagger_utils.drf_server.utils.server_gen.get_api_environment import get_api_environment
    view_environment = get_api_environment(app_name, endpoint_name, group_name)
    from django_swagger_utils.drf_server.utils.constants import CONSTANTS

    if view_environment == CONSTANTS["ENV_MOCK"]:
        if group_name:
            view = getattr(importlib.import_module(
                "%s.build.mock_views.%s.%s.%s" % (
                    app_name, group_name, endpoint_name, endpoint_name)),
                endpoint_name)
        else:
            view = getattr(importlib.import_module(
                "%s.build.mock_views.%s.%s" % (
                    app_name, endpoint_name, endpoint_name)), endpoint_name)
        response_object = view(*args, **kwargs)
    elif view_environment == CONSTANTS["ENV_IMPL"]:
        if group_name:
            view = getattr(importlib.import_module(
                "%s.views.%s.%s.%s" % (
                    app_name, group_name, endpoint_name, endpoint_name)),
                endpoint_name)
        else:
            view = getattr(importlib.import_module(
                "%s.views.%s.%s" % (app_name, endpoint_name, endpoint_name)),
                           endpoint_name)
        response_object = view(*args, **kwargs)
    else:
        from django_swagger_utils.drf_server.exceptions.view_enviroment_not_defined_error import \
            ViewEnvironmentNotDefinedError
        raise ViewEnvironmentNotDefinedError("View Environment not defined")
    return response_object
