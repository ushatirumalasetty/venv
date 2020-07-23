
class SwaggerParser(object):
    """
    we validate and pass every element of the spec file in the below methods
    """

    def __init__(self, spec_json):
        '''

        :param spec_json: spec file
        '''
        self.sepc_json = spec_json

    def consumes(self):
        return self.sepc_json.get("consumes", [])

    def produces(self):
        return self.sepc_json.get("produces", [])

    def definitions(self):
        """
        validate for definition names and property names
        if valid return deinitions dict
        :return:
        """
        for key in self.sepc_json.get("definitions", {}):
            self.check_for_validation("definition", key)
            if "properties" in self.sepc_json.get("definitions", {})[key]:
                for each_property in self.sepc_json.get("definitions", {})[key]["properties"]:
                    self.check_for_validation("property name", each_property)
        return self.sepc_json.get("definitions", {})

    def security_definitions(self):
        """

        :return: security def dict
        """
        return self.sepc_json.get("securityDefinitions", {})

    def security(self):
        """
        return list of scopes required
        :return:
        """
        return self.sepc_json.get("security", [])

    def parameters(self):
        """
        validate for parameter names
        if valid return parameters dict
        :return:
        """
        for key in self.sepc_json.get("parameters", {}):
            self.check_for_validation("parameter", self.sepc_json.get("parameters", {})[key]["name"])

        return self.sepc_json.get("parameters", {})

    def responses(self):
        """
        validate for response names
        if valid return response dict
        :return:
        """
        for key in self.sepc_json.get("responses", {}):
            self.check_for_validation("response", key)
        return self.sepc_json.get("responses", {})

    def paths(self):
        """
               validate for elements in all paths and methods of each path
               if valid return paths dict
               :return:
               """
        for key in self.sepc_json.get("paths", {}):
            if "parameters" in self.sepc_json.get("paths", {})[key]:
                for each_param in self.sepc_json.get("paths", {})[key]["parameters"]:
                    if "name" in each_param:
                        self.check_for_validation("parameter", each_param["name"])
            method_list = ["get", "post", "delete", "put"]
            for each_method in method_list:
                if each_method in self.sepc_json.get("paths", {})[key]:
                    self.check_for_validation("operationId",
                                              self.sepc_json.get("paths", {})[key][each_method]["operationId"])
                    if "parameters" in self.sepc_json.get("paths", {})[key][each_method]:

                        param_list = self.sepc_json.get("paths", {})[key][each_method]["parameters"]
                        for each_param in param_list:
                            if "name" in each_param:
                                self.check_for_validation("parameter", each_param["name"])

        return self.sepc_json.get("paths", {})

    def api_base_path(self):
        """

        :return: base path of the app
        """
        return self.sepc_json.get("basePath", "/")

    def check_for_validation(self, item, item_name):
        """
        we check if the elements are valid
        a element is considered invalid if it contains a white space or other unappropriate symbols for programming
        it is also invalid if it contains keywords of java or js
        :param item: a spec file element ,could be response,parameter,definition or any other
        :param item_name: the name of the element which is subjected to test
        :return:
        """
        # TODO add more invalid symbols in parameter name
        invalid_symbol = [' ', '-']
        # check for all symbols
        for each_symbol in invalid_symbol:
            if each_symbol in item_name:
                if each_symbol == ' ':
                    print('Invalid name for ' + item + " " + item_name + "\" \ncannot contain a white space")

                else:
                    print('Invalid name for ' + item + " " + item_name + "\ncannot contain a " + each_symbol)
                print("BUILD FAILURE")
                exit(1)
        reserved_words = ["abstract", "assert", "boolean", "break", "byte", "switch", "case", "try", "catch", "finally",
                          "char", "class", "continue", "default", "do", "double", "if", "else", "extends", "final",
                          "float", "for", "implements", "import", "instanceOf", "int", "interface", "long", "native",
                          "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp",
                          "super", "synchronized", "this", "throw", "throws", "transient", "void", "volatile", "while",
                          "goto", "const", "enum", "default", "eval", "export", "let", "await", "with", "typeof",
                          "yield", "function", "debugger", "in"]
        # check for all reserved words
        for each_word in reserved_words:
            if item_name == each_word:
                print('Invalid name for ' + item + " " + item_name + "\ncannot be a keyword in java")
                print("BUILD FAILURE")

                exit(1)
