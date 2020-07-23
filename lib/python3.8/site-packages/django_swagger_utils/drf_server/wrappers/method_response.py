class MethodResponse(object):
    def __init__(self, response_json, response_obj=None, response_headers_obj=None, response_headers_json=None,
                 response_code=200):
        # todo convert endpoint_response method to Method response object
        self.response_json = response_json
        self.response_obj = response_obj
        self.response_headers_obj = response_headers_obj
        self.response_headers_json = response_headers_json
        self.response_code = response_code
