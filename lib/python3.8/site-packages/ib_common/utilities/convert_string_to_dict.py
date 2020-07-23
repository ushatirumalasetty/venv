def convert_string_to_dict(input_string):
    import ast
    try:
        input_dict = ast.literal_eval(input_string)
    except:
        input_dict = {}
    return input_dict
