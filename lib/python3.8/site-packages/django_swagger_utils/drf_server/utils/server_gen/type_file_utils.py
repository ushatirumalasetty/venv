def get_type_object(validated_data, type_file_class, field_name):
    try:
        _data = validated_data.pop(field_name)
        _object = type_file_class(**_data)
    except:
        _object = None
    return _object


def get_type_list_object(validated_data, type_file_class, field_name):
    _list = []
    try:
        _list_data = validated_data.pop(field_name)
    except:
        _list_data = []
    for item in _list_data:
        _list.append(type_file_class(**item))
    return _list
