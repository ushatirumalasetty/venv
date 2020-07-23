import importlib
from abc import ABCMeta
from abc import abstractmethod

from django_swagger_utils.drf_server.decorators.handle_exceptions import handle_exceptions
from future.utils import with_metaclass


class ValidatorAbstractClass(with_metaclass(ABCMeta, object)):
    # Abstract class which every validator class should inherit
    @abstractmethod
    def validate(self):
        pass


def validate_decorator(validator_class):
    # validate_decorator
    def decorator(func):
        def handler(*args, **kwargs):
            if not issubclass(validator_class, ValidatorAbstractClass):
                raise Exception('Validator class should inherit ValidatorAbstractClass')
            if validator_class is None:
                raise Exception('Validator class cannot be none')
            validator = validator_class(*args, **kwargs)
            validation_output = validator.validate()
            kwargs['validation_output'] = validation_output
            return func(*args, **kwargs)

        handler.__doc__ = func.__doc__
        return handler

    return decorator


def interface_decorator(app_name, httpmethod, urltail, methodname):
    def set_input_variables(func):
        @handle_exceptions()
        def handler(*args, **kwargs):
            obj = args[0]
            setattr(obj, 'request_data', kwargs.get('request_data', None))
            setattr(obj, 'path_params', kwargs.get('path_params', None))
            setattr(obj, 'query_params', kwargs.get('query_params', None))
            setattr(obj, 'headers_obj', kwargs.get('headers_obj', None))
            setattr(obj, 'request_type', httpmethod)
            setattr(obj, 'url_tail', urltail)

            def api_wrapper(*args, **kwargs):
                import_str = app_name + '.views.' + methodname + '.api_wrapper'
                api_wrapper = getattr(importlib.import_module(import_str), 'api_wrapper')
                return api_wrapper(*args, **kwargs)

            setattr(obj, 'api_wrapper', api_wrapper)
            handler.__doc__ = func.__doc__
            return obj.execute()

        return handler

    return set_input_variables
