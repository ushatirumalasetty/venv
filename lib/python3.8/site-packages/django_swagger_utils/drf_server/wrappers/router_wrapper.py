# coding=utf-8
import importlib


def router_wrapper(app_name, url_path, operations_dict, request, *args, **kwargs):
    view_name = operations_dict.get(request.method, None)
    if view_name:

        import_str = "%s.build.view_environments.%s.%s.%s" % (app_name, url_path,view_name, view_name)

        view_def = getattr(importlib.import_module(import_str), view_name)
        response = view_def(request, *args, **kwargs)
    else:
        from django.http import HttpResponse
        from rest_framework import status
        return HttpResponse("Method Not Allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return response
