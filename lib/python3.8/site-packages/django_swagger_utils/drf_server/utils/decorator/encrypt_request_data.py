def encrypt_request_data(wrapper_request_object):
    from django.conf import settings
    from django_swagger_utils.drf_server.utils.decorator.get_private_key_then_verify import get_private_key_then_verify
    from django_swagger_utils.drf_server.utils.decorator.getDecryptedData import getDecryptedData

    client_key_details_id = wrapper_request_object.clientKeyDetailsId
    json_data_string = wrapper_request_object.data

    private_key = get_private_key_then_verify(client_key_details_id)

    django_swagger_utils_settings = settings.SWAGGER_UTILS

    defaults = django_swagger_utils_settings["DEFAULTS"]
    get_decrypted_data = defaults.get("GET_DECRYPTED_DATA_FUNCTION", getDecryptedData)

    decrypted_json_data_string = get_decrypted_data(private_key, json_data_string)
    return decrypted_json_data_string
