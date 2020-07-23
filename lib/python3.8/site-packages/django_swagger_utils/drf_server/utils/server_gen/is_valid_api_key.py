# coding=utf-8
from rest_framework import permissions


class IsValidAPIKeyBase(permissions.BasePermission):
    """
    Validate API Key
    """
    message = 'not a valid api key.'

    def __init__(self, name, is_header=False):
        """

        :param name:
        :param is_header:
        """
        self.is_header = is_header
        self.name = name

    def has_permission(self, request, view):
        """

        :param request:
        :param view:
        :return:
        """
        if self.is_header:
            self.name = "HTTP_%s" % self.name.replace("-", "_").upper()
            api_key = request.META.get(self.name, None)
        else:
            api_key = request.query_params.get(self.name, None)
        return self.validate_api_key(api_key)

    @staticmethod
    def validate_api_key(api_key):
        """

        :param api_key:
        :return:
        """
        if api_key:
            # todo need implement api_key validation
            return True
        return False


def IsValidAPIKey(name, kwargs, IsValidAPIKeyBase=IsValidAPIKeyBase):
    """
    ref http://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class

    """

    def __init__(self):
        IsValidAPIKeyBase.__init__(self, **kwargs)

    new_class = type(name, (IsValidAPIKeyBase,), {"__init__": __init__})
    return new_class
