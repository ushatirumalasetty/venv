def get_unicode_str(instance):
    parameters = dir(instance)
    parameters = [name for name in parameters if not name.startswith("__")]
    parameter_dict = dict()
    for each_parameter in parameters:
        parameter_dict[each_parameter] = getattr(instance, each_parameter)
    return str(parameter_dict)
