from django_swagger_utils.drf_server.fields.boolean_field import boolean_field
from django_swagger_utils.drf_server.fields.integer_field import integer_field
from django_swagger_utils.drf_server.fields.number_field import number_field
from django_swagger_utils.drf_server.fields.string_field import string_field


def get_array_field(array_param, array_name, collection_format, return_example=False):
    array_param_type = array_param.get("type", None)

    from django_swagger_utils.drf_server.utils.server_gen.collection_fromat_to_separator import \
        collection_format_to_separator
    separator = collection_format_to_separator(collection_format)
    if not array_param:
        raise Exception("property 'type' not defined for array filed : '%s' " % array_name)
    if array_param_type == "integer":
        child_str, example = integer_field(array_param, return_example=True)
    elif array_param_type == "number":
        child_str, example = number_field(array_param, return_example=True)
    elif array_param_type == "string":
        child_str, example = string_field(array_param, return_example=True)
    elif array_param_type == "boolean":
        child_str, example = boolean_field(array_param, return_example=True)
    elif array_param_type == "array":
        inner_collection_format = array_param.get("collectionFormat", "csv")
        inner_array_param = array_param.get("items")
        child_str, example = get_array_field(inner_array_param, array_name, inner_collection_format,
                                             return_example=True)
    else:
        raise Exception("Unsupported array field type: choices [integer, string, number, boolean, array]")
    param_serializer_field = "CollectionFormatField(separator='%s', child=%s)" % (separator, child_str)
    if return_example:
        return param_serializer_field, [example]
    return param_serializer_field
