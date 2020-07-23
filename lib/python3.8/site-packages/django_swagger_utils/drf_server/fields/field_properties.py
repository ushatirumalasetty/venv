def field_properties(properties):
    format = properties.get("format", None)
    # int32, int64, float, double, byte, binary, date, date-time, password

    # valid only in query, form data
    allow_empty_values = properties.get("allowEmptyValue", None)

    # collectionFormat
    # support for collection format - multi needs to update the request_response wrapper
    collection_format = properties.get("collectionFormat", None)

    default = properties.get("default", None)

    maximum = properties.get("maximum", None)
    exclusive_maximum = properties.get("exclusiveMaximum", None)

    minimum = properties.get("minimum", None)
    exclusive_minimum = properties.get("exclusiveMinimum", None)

    max_length = properties.get("maxLength", None)
    min_length = properties.get("minLength", None)

    # not supported in the automation
    pattern = properties.get("pattern", None)

    max_items = properties.get("maxItems", None)
    min_items = properties.get("minItems", None)

    unique_items = properties.get("uniqueItems", None)
    enum = properties.get("enum", None)

    multiple_of = properties.get("multipleOf", None)

    description = properties.get("description", None)
