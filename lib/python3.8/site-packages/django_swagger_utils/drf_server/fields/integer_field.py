import random


def integer_field(properties, required=True, return_example=False):
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
    # int32, int64
    format = properties.get("format", None)

    max_integer = 1000
    maximum = properties.get("maximum", None)
    if maximum is not None:
        max_integer = maximum
        options_list.append("max_value=%d" % maximum)

    # not supported
    exclusive_maximum = properties.get("exclusiveMaximum", None)
    min_interger = 0
    minimum = properties.get("minimum", None)
    if minimum is not None:
        min_interger = minimum
        options_list.append("min_value=%d, " % minimum)

    # not supported
    exclusive_minimum = properties.get("exclusiveMinimum", None)

    int_field = 'serializers.IntegerField(%s)' % ", ".join(options_list)
    if return_example:
        sample_integer = min_interger
        if min_interger != max_integer:
            sample_integer = random.randrange(min_interger, max_integer)
        default = default if default else sample_integer
        return int_field, default
    return int_field
