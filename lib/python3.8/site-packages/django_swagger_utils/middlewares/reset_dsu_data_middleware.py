# from django

from django.utils.deprecation import MiddlewareMixin


def reset_dsu_data():
    from django_swagger_utils import local
    try:
        del local.user_id
        del local.app_name
        del local.operation_id
        del local.api_execution_time
    except AttributeError:
        pass


class ResetDSUDataMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        reset_dsu_data()
        return response

    def process_exception(self, request, exception):
        reset_dsu_data()
