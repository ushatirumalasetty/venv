import logging

from django_swagger_utils import local

"""
    this is a custom log filters

    usage:

    settings.py

    LOGGING['filters'].update({
        'user_id': {
            '()': 'django_swagger_utils.logger.log_filters.UserIDFilter'
        },
        'operation_id': {
            '()': 'django_swagger_utils.logger.log_filters.OperationIdFilter'
        },
        'app_name': {
            '()': 'django_swagger_utils.logger.log_filters.AppNameFilter'
        }
    })



"""


class UserIDFilter(logging.Filter):

    def filter(self, record):
        record.user_id = getattr(local, 'user_id', 'GUEST')
        return True


class OperationIdFilter(logging.Filter):

    def filter(self, record):
        record.operation_id = getattr(local, 'operation_id', '')
        return True


class AppNameFilter(logging.Filter):

    def filter(self, record):
        record.app_name = getattr(local, 'app_name', '')
        return True
