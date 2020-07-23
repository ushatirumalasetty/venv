__author__ = 'kapeed2091'


def get_file_name(file_obj):
    try:
        file_name = file_obj.name
    except AttributeError:
        file_name = ''
    return file_name
