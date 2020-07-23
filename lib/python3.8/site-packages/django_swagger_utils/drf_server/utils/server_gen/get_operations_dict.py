import re


def get_operations_dict(path_method_dict, request_path):
    operation_dict = None
    for path_regex, method_dict in list(path_method_dict.items()):
        if re.match(r'.*{}'.format(path_regex), request_path):
            operation_dict = method_dict
            break
    if not operation_dict:
        raise Exception("{} : operation dict not found".format(request_path))
    return operation_dict
