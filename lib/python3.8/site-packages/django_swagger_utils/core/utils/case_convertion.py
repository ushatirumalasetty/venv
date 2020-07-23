def str_to_snake_case(s):
    import re
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', s).lower()


def to_camel_case(str_to_convert):
    components = str_to_snake_case(str_to_convert).split('_')
    return components[0].title() + "".join(x.title() for x in components[1:])


def camel_to_snake(camel):
    """
    Converts CamelCase names to snake_case
    :param camel:
    :return:
    """
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(snake):
    """
    Converts snake_case to CamelCase
    :param snake:
    :return:
    """
    snake = '_'.join([s.capitalize() for s in snake.split()])
    return ''.join([s.capitalize() for s in snake.split('_')])


def hyphen_to_camel(hyphen):
    """
    Converts hyphen-case to CamelCase
    :param hyphen:
    :return:
    """
    hyphen = '-'.join([s.capitalize() for s in hyphen.split()])
    return ''.join([h.capitalize() for h in hyphen.split('-')])
