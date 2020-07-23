def convert_path_to_package_str(full_path_to_module, base_dir=None):
    """
    converts to a programmable format by replacing / with .
    :param full_path_to_module: path of a file
    :param base_dir:
    :return:
    """
    from django.conf import settings
    import os

    if not base_dir:
        base_dir = settings.BASE_DIR
    relpath_to_module = os.path.relpath(full_path_to_module, base_dir)
    # print relpath_to_module, full_path_to_module, base_dir
    module_dir, module_file = os.path.split(relpath_to_module)
    module_name, module_ext = os.path.splitext(module_file)
    package_str = "{0}.{1}".format(".".join(module_dir.split("/")), module_name)
    return package_str
