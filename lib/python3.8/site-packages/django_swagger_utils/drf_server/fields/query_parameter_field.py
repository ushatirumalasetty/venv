from django_swagger_utils.drf_server.fields.boolean_field import boolean_field
from django_swagger_utils.drf_server.fields.integer_field import integer_field
from django_swagger_utils.drf_server.fields.number_field import number_field
from django_swagger_utils.drf_server.fields.string_field import string_field


def query_param_field(param, parameter_key_name=None):


    param_name = param["name"]

    if not parameter_key_name:
        parameter_key_name = param_name
    from django_swagger_utils.core.utils.case_convertion import to_camel_case
    context_properties = {
        "param_name_camel_case": to_camel_case(param_name),
        "param_name": parameter_key_name,
        "param_field_name": param_name,
        "param_serializer": "",
        "param_serializer_import_str": "",
        "param_serializer_field": "",
        "param_url_regex": "",
        "param_example" : ""
    }

    param_type = param.get("type", None)
    param_required = param.get("required", False)

    if not param_type:
        raise Exception("property 'type' not defined for query param  %s : %s" % (param_name, parameter_key_name))
    if param_type == "integer":
        context_properties["param_serializer_field"], context_properties["param_example"] = \
            integer_field(param, param_required, return_example=True)

    elif param_type == "number":
        context_properties["param_serializer_field"], context_properties["param_example"] = \
            number_field(param, param_required, return_example=True)
    elif param_type == "string":
        context_properties["param_serializer_field"], context_properties["param_example"] = \
            string_field(param, param_required, return_example=True)
    elif param_type == "boolean":
        context_properties["param_serializer_field"], context_properties["param_example"] = \
            boolean_field(param, param_required, return_example=True)
    elif param_type == "array":
        collection_format = param.get("collectionFormat", "csv")

        from django_swagger_utils.drf_server.fields.collection_array_field import get_array_field
        context_properties["param_serializer_field"], context_properties["param_example"] = \
            get_array_field(param.get("items"), param_name, collection_format, return_example=True)
    else:
        raise Exception("Invalid value for type of query param")
    return context_properties
