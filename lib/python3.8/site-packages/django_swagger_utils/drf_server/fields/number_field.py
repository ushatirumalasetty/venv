import random


def number_field(properties, required=True, return_example=False):
    options_list = []

    if not required:
        options_list.append("required=False")
        options_list.append("allow_null=True")

    description = properties.get("description", None)
    if description:
        options_list.append("help_text=\"%s\"" % description)

    default = properties.get("default", None)
    if default:
        options_list.append("default=%s" % default)

    # not supported
    # float, double
    format = properties.get("format", None)

    max_value = 1000.0
    maximum = properties.get("maximum", None)
    if maximum is not None:
        max_value = maximum
        options_list.append("max_value=%f" % maximum)

    # not supported
    exclusive_maximum = properties.get("exclusiveMaximum", None)

    min_value = 0
    minimum = properties.get("minimum", None)
    if minimum is not None:
        min_value = minimum
        options_list.append("min_value=%f" % minimum)

    # not supported
    exclusive_minimum = properties.get("exclusiveMinimum", None)

    num_field = 'serializers.FloatField(%s)' % ", ".join(options_list)
    if return_example:
        sample_value = min_value
        if min_value != max_value:
            sample_value = random.randrange(min_value, max_value)
        default = default if default else sample_value
        return num_field, default
    return num_field
