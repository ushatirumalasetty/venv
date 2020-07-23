__author__ = 'kapeed'


def is_null_or_empty(field_name):
    if field_name is not None and field_name.strip() != "":
        return False
    return True
