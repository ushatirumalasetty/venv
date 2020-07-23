def body_field(param, paths, base_path, parameter_key_name=None,
               swagger_definitions=None):
    param_required = param.get("required", False)

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
        "param_serializer_required": param_required,
        "param_serializer_array": False,
    }

    param_schema = param.get("schema", None)

    if not param_schema:
        raise Exception(
            "property 'schema' not defined for form body param : %s : %s" % (
                param_name, parameter_key_name))
    else:

        # if swagger_definitions: # no need to check for swagger definitions

        from django_swagger_utils.core.generators.swagger_sample_schema import \
            SwaggerSampleSchema
        swagger_sample_json = SwaggerSampleSchema(swagger_definitions,
                                                  param_schema)
        sample_json = swagger_sample_json.to_json()
        context_properties["param_serializer_sample_json"] = sample_json

        # checks if reference
        to_file = True
        if '$ref' in param_schema:
            to_file = False

        from django_swagger_utils.drf_server.utils.server_gen.get_object_properties import \
            get_object_properties
        object_properties = get_object_properties(prop_name=param_name,
                                                  schema_properties=param_schema,
                                                  paths=paths,
                                                  base_path=base_path,
                                                  to_file=to_file)
        context_properties["param_serializer"] = object_properties[
            "field_string"]
        context_properties["param_serializer_import_str"] = object_properties[
            "serializer_import_str"]
        context_properties["param_serializer_array"] = object_properties[
            "is_array_serializer"]
    return context_properties
