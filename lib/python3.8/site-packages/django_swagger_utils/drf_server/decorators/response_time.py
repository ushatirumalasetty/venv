# coding=utf-8


import json
import logging

from past.utils import old_div

logger = logging.getLogger('dsu.debug')


def get_db_time(queries):
    total_time = 0
    from collections import OrderedDict
    queries_data = OrderedDict()
    duplicate_total_queries = 0
    duplicate_unique_queries = 0
    for query in queries:
        query_time = query.get('time')
        if query_time is None:
            # django-debug-toolbar monkeypatches the connection
            # cursor wrapper and adds extra information in each
            # item in connection.queries. The query time is stored
            # under the key "duration" rather than "time" and is
            # in milliseconds, not seconds.
            query_time = old_div(query.get('duration', 0), 1000)
        total_time += float(query_time)
        if query["sql"] not in queries_data:
            queries_data[query["sql"]] = {"count": 1,
                                          "time": float(query_time)}
        else:
            if queries_data[query["sql"]]["count"] == 1:
                duplicate_unique_queries += 1
            duplicate_total_queries += 1
            queries_data[query["sql"]]["count"] += 1
            queries_data[query["sql"]]["time"] += float(query_time)

    queries_data = json.dumps(queries_data)
    return total_time, duplicate_unique_queries, queries_data, \
           duplicate_total_queries


def _get_response(response):
    from django.http import HttpResponse
    from rest_framework.response import Response
    if isinstance(response, Response):
        result = response.data
    elif isinstance(response, HttpResponse):
        result = response._container[0].decode('utf-8')
    else:
        result = response.data
    from django_swagger_utils.drf_server.decorators.request_response import \
        mask_sensitive_info
    return {
        "status_code": response.status_code,
        "headers": response._headers,
        "cookies": response.cookies,
        "response_data": mask_sensitive_info(result)
    }


def handle_8kb_log_limit_response_log(_dict):
    max_response_data_size = 6000
    api_response_log_message = json.dumps(_dict)
    import math
    max_range = int(math.ceil(
        len(api_response_log_message) / float(max_response_data_size)
    ))
    for i in range(max_range):
        logger.debug(
            api_response_log_message[
            i * max_response_data_size:  (i + 1) * max_response_data_size])


def response_time(app_name, operation_id):
    """

    :return:
    """

    def decorator(function):
        """

        :param function:
        :return:
        """

        def handler(*args, **kwargs):
            from time import time
            start_time = time()
            from django.db import connection
            return_value = function(*args, **kwargs)
            end_queries = connection.queries
            db_queries_count = len(end_queries)
            db_time, duplicate_queries, db_queries, total_db_queries = \
                get_db_time(end_queries)
            end_time = time()
            total_time = end_time - start_time

            from django.conf import settings
            if getattr(settings, 'LOG_DSU_OLD_VERSION_LOGS', True):
                _dict = {
                    "App Name": app_name,
                    "OperationId": operation_id,
                    "EndpointResponseTime": total_time,
                    "TotalDBQueries": db_queries_count
                }
                logger.debug(_dict)

            from django_swagger_utils import local
            _dict = {
                "api_execution_time": getattr(local, 'api_execution_time', 0),
                "total_db_queries": total_db_queries,
                "db_queries_execution_time": db_time,
                "endpoint_response_time": total_time,
                "log_type": "api_response"
            }
            _dict.update(_get_response(return_value))

            from django.conf import settings
            if getattr(settings, 'LOG_DETAILED_REQUEST_RESPONSE', True):
                handle_8kb_log_limit_response_log(_dict)

            from django.conf import settings
            if getattr(settings, 'STORE_LATENCY_OBJECT', True):
                from django_swagger_utils.models import Latency
                Latency.objects.create(
                    app_name=app_name,
                    operation_id=operation_id,
                    response_time=total_time,
                    db_queries_count=db_queries_count,
                    db_queries=db_queries,
                    db_time=db_time,
                    duplicate_queries=duplicate_queries,
                    total_duplicate_queries=total_db_queries
                )
            return return_value

        handler.__doc__ = function.__doc__
        return handler

    return decorator
