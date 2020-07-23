def get_path_param_from_regex(url_string):
    import re
    index = url_string.find("{")
    param_name = ""
    if index != -1:
        p = re.compile(r"^(.*)(\{)(.*)(\})(.*)$")
        m = p.match(url_string)
        groups = m.groups()
        param_name = groups[3]
    return param_name