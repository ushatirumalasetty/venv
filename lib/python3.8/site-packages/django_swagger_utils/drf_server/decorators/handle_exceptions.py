# coding=utf-8

import logging

logger = logging.getLogger('dsu.debug')


def handle_exceptions():
    """

    :return:
    """

    def decorator(function):
        """

        :param function:
        :return:
        """

        def handler(*args, **kwargs):

            try:
                function_return_value = function(*args, **kwargs)
                return function_return_value
            except Exception as err:

                import traceback
                logger.info(traceback.format_exc())

                error_class_name = err.__class__.__name__
                from django_swagger_utils.drf_server.utils.decorator.handle_custom_exceptions import \
                    CUSTOM_EXCEPTIONS_DICT
                if error_class_name in list(CUSTOM_EXCEPTIONS_DICT.keys()):
                    from django_swagger_utils.drf_server.utils.decorator.handle_custom_exceptions import \
                        get_status_code_content_library
                    data = get_status_code_content_library(CUSTOM_EXCEPTIONS_DICT, err, 500)
                    return data
                raise err

        handler.__doc__ = function.__doc__
        return handler

    return decorator
