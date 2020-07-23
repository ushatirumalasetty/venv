import os

from django_swagger_utils.core.utils.case_convertion import to_camel_case


def get_test_cases_dict(tests_dir_path, operation_name):
    camel_case_operation_name = to_camel_case(operation_name)
    from collections import OrderedDict
    test_cases = OrderedDict()
    default_test_case = "test_case_01.py"
    try:
        dir_list = sorted(os.listdir(tests_dir_path))
    except OSError as err:
        dir_list = [default_test_case]
    for dl in dir_list:
        if 'test_case_' in dl:
            test_case = dl.split(".")[0]
            test_cases[test_case] = to_camel_case(test_case) + camel_case_operation_name + "APITestCase"
    if not test_cases:
        test_case = default_test_case.split(".")[0]
        test_cases[test_case] = to_camel_case(test_case) + camel_case_operation_name + "APITestCase"
    return test_cases
