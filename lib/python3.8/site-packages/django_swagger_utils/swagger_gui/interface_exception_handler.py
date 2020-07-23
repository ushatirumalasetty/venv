__author__ = 'tanmay.ibhubs'


def handle_interface_exception(response):
    """

    :param response:
    :return: prints the error based on interface exception, then returns
    """
    if not response:
        return

    if type(response) != dict:
        return

    from colored import fg, attr
    http_status_code = response.get('http_status_code', None)
    if http_status_code == 403:
        print('{}{}{}Access Forbidden: {}'.format(
            fg(1), attr(1), attr(4), response.get("response", "")))

    elif http_status_code == 404:
        print('{}{}{}Not Found: {}'.format(
            fg(1), attr(1), attr(4), response.get("response", "")))

    elif http_status_code == 417:
        print('{}{}{}Expectation Failed: {}'.format(
            fg(1), attr(1), attr(4), response.get("response", "")))

    elif http_status_code == 401:
        print('{}{}{}Unauthorized: {}'.format(
            fg(1), attr(1), attr(4), response.get("response", "")))

    elif http_status_code == 400:
        print('Bad Request : {}'.format(
            fg(1), attr(1), attr(4), response.get("response", "")))
    else:
        return
