def drf_json_parser(json_data_string):
    import ast
    try:
        import json
        json_data_dict = json.loads(json_data_string[1:-1])
        return json_data_dict
    except ValueError:
        json_data_dict = ast.literal_eval(json_data_string)

    from io import BytesIO
    from rest_framework.parsers import JSONParser

    json_data_bytes = json_data_dict.encode()
    stream = BytesIO(json_data_bytes)

    data = JSONParser().parse(stream)
    return data
