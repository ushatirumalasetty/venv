import importlib


def get_use_cases_list(app_name, operation_name):
    try:
        import_str = "%s.conf.use_cases.%s" % (app_name, operation_name)
        use_cases_list = getattr(importlib.import_module(import_str), "USE_CASES_LIST")
    except ImportError:
        use_cases_list = []
    return use_cases_list
