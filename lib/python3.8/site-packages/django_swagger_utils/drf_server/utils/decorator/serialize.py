def serialize(serializer_class, input_type_obj, **kwargs):
    if serializer_class:
        serializer = serializer_class(input_type_obj, **kwargs)
        return serializer.data
    return None
