def handle_interface_exception(response):
    from django_swagger_utils.drf_server.exceptions.forbidden import Forbidden
    from django_swagger_utils.drf_server.exceptions.not_found import NotFound
    from django_swagger_utils.drf_server.exceptions.expectation_failed import ExpectationFailed
    from django_swagger_utils.drf_server.exceptions.unauthorized import Unauthorized
    from django_swagger_utils.drf_server.exceptions.bad_request import BadRequest
    if not response:
        return

    if type(response) != dict:

        return

    http_status_code = response.get('http_status_code', None)
    if http_status_code == 403:
        raise Forbidden(response.get("response", ""), res_status=False)
    elif http_status_code == 404:
        raise NotFound(response.get("response", ""), res_status=False)
    elif http_status_code == 417:
        raise ExpectationFailed(response.get("response", ""), res_status=False)
    elif http_status_code == 401:
        raise Unauthorized(response.get("response", ""), res_status=response["res_status"])
    elif http_status_code == 400:
        raise BadRequest(response.get("response", ""), res_status=False)
    else:
        return
