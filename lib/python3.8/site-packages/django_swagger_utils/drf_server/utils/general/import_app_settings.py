def import_app_settings(app_name):
    import importlib
    my_module = importlib.import_module("%s.conf.settings" % app_name)
    module_dict = my_module.__dict__
    try:
        to_import = my_module.__all__
    except AttributeError:
        to_import = [name for name in module_dict if not name.startswith('_')]
    out = {
        "module_dict": module_dict,
        "to_import": to_import
    }
    return out
