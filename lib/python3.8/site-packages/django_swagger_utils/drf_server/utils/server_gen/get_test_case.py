
import importlib


def get_test_case(app_name, operation_name, test_case_name):
    try:
        import_str = "%s.conf.test_cases.%s.%s" % (app_name, operation_name, test_case_name)
        test_case = getattr(importlib.import_module(import_str), "TEST_CASE")
    except ImportError as err:
        print(err)
        raise
    return test_case
