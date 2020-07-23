from django_swagger_utils.drf_server.fields.boolean_field import boolean_field
from django_swagger_utils.drf_server.fields.integer_field import integer_field
from django_swagger_utils.drf_server.fields.number_field import number_field
from django_swagger_utils.drf_server.fields.string_field import string_field


def form_param_field(param, parameter_key_name):
    # repeated code from self.query_param_field, self.header_field
    # to maintain the less coupling between parameter types


    param_name = param["name"]
    from django_swagger_utils.core.utils.case_convertion import to_camel_case
    context_properties = {
        "param_name_camel_case": to_camel_case(param_name),
        "param_name": parameter_key_name,
        "param_field_name": param_name,
        "param_serializer": "",
        "param_serializer_import_str": "",
        "param_serializer_field": "",
        "param_url_regex": ""
    }

    param_type = param.get("type", None)
    param_required = param.get("required", False)

    if not param_type:
        raise Exception("property 'type' not defined for form param :%s : %s" % (param_name, parameter_key_name))
    if param_type == "integer":
        context_properties["param_serializer_field"] = integer_field(param, param_required)
    elif param_type == "number":
        context_properties["param_serializer_field"] = number_field(param, param_required)
    elif param_type == "string":
        context_properties["param_serializer_field"] = string_field(param, param_required)
    elif param_type == "boolean":
        context_properties["param_serializer_field"] = boolean_field(param, param_required)
    elif param_type == "array":
        collection_format = param.get("collectionFormat", "csv")

        from django_swagger_utils.drf_server.fields.collection_array_field import get_array_field
        context_properties["param_serializer_field"] = get_array_field(param.get("items"), param_name,
                                                                       collection_format)
    else:
        raise Exception("Invalid value for type of form param")
    return context_properties
