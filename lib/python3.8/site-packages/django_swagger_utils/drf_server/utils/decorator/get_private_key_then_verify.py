def get_private_key_then_verify(client_key_details_id):
    from django.conf import settings
    django_swagger_utils_settings = settings.SWAGGER_UTILS
    from django_swagger_utils.drf_server.utils.decorator.getPrivateKeyFromClientKeyRelatedDetails import \
        getPrivateKeyFromClientKeyRelatedDetails

    defaults = django_swagger_utils_settings["DEFAULTS"]
    get_private_key_from_client_key_related_details = defaults.get("GET_CLIENT_KEY_DETAILS_FUNCTION",
                                                                   getPrivateKeyFromClientKeyRelatedDetails)

    private_key = get_private_key_from_client_key_related_details(client_key_details_id)
    if private_key is None:
        error_message = 'Invalid client key details Id'
        from django_swagger_utils.drf_server.exceptions.client_key_error import ClientKeyError
        raise ClientKeyError(error_message)
    return private_key
