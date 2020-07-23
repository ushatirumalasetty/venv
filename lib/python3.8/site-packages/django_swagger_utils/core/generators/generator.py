class Generator(object):
    def __init__(self, app_name, parser, paths, base_path):
        self.app_name = app_name
        self.parser = parser
        self.paths = paths
        self.base_path = base_path

    @staticmethod
    def snake_to_camel_case(a):
        """
        converts naming to a programming format
        for example if a name has two words we seperate the words using '_'in spec file
        whereas the words are sperated by indicating the beginning of next word with a uppar case letter
        :param a:
        :return:
        """
        camel_case = ""
        for k in a.split("_"):
            camel_case = camel_case + k[0].capitalize() + k[1:]
        return camel_case

    @staticmethod
    def get_name_from_reference(reference):
        import re
        def_name = re.split("[#a-zA-Z]*/", reference)
        return def_name[len(def_name) - 1]

    @staticmethod
    def get_variable_name_for_definition(s):
        return s[:1].lower() + s[1:] if s else ''

    @staticmethod
    def is_array(s):
        """
        returns true if given parameter is an array
        :param s:
        :return:
        """
        if '[]' in s:
            return True
        else:
            return False

    @staticmethod
    def remove_array_notation_from_name(a):
        return a.replace("[]", "")

    def get_request_parameters(self, method_props):
        """
        get requests parameters from spec file
        :param method_props:
        :return:
        """
        req_parameters = {}
        if 'parameters' in method_props:
            parameters = method_props.get("parameters")
            for params in parameters:
                if '$ref' in params:
                    param_name = self.get_name_from_reference(params.get("$ref"))

                    req_parameters = self.merge_dicts(req_parameters, self.get_parameters_from_reference(param_name))
                if params.get("in") == "body":
                    param_required = params.get("required", False)
                    param_name = "body"
                    req_parameters = self.merge_dicts(req_parameters,
                                                      self.filter_body_name_from_parameters(
                                                          self.get_dict_from_each_property(params.get("schema"),
                                                                                           param_name, "",
                                                                                           param_required)))
        return req_parameters

    def get_parameters_from_reference(self, pn):
        """
        returns paramters mentioned in spec file under "parameters"
        :param pn:
        :return:
        """
        req_parameters = {}
        for param_name, params in list(self.parser.parameters().items()):
            if (param_name == pn) and (params.get('in') == "body"):
                param_required = params.get("required", False)
                param_name = "body"
                req_parameters = self.filter_body_name_from_parameters(
                    self.get_dict_from_each_property(params.get("schema"), param_name,
                                                     "", param_required))
        return req_parameters

    def get_definition_parameters(self, model_name):
        """
        returns defination properties and required properties
        :param model_name:
        :return:
        """
        model_parameters = {}
        for def_name, definition in list(self.parser.definitions().items()):
            if def_name == model_name:
                if 'properties' in definition:
                    props = definition.get("properties")

                    required_list = definition.get("required", [])
                    model_parameters = self.get_dict_from_properties(props, "", required_list)

                elif 'allOf' in definition:
                    model_parameters = self.filter_body_name_from_parameters(
                        self.get_dict_from_each_property(definition, "body"))
        return model_parameters

    def get_response_parameters(self, method_props):
        """
        returns parameters in response body
        :param method_props:
        :return:
        """
        res_parameters = {}
        if ("200" or "default") in method_props.get("responses"):
            response = method_props.get("responses").get("200")
            if 'schema' in response:
                res_parameters = self.get_dict_from_each_property(response.get("schema"), "body")
            elif '$ref' in response:
                res = self.get_name_from_reference(response.get("$ref"))
                for res_name, resp in list(self.parser.responses().items()):
                    if res == res_name:
                        res_parameters = self.get_dict_from_each_property(resp.get("schema"), "body")
        res_parameters = self.filter_body_name_from_parameters(res_parameters)
        return res_parameters

    @staticmethod
    def merge_dicts(x, y):
        """
        merges two dictionaries and returns the resultant
        :param x:
        :param y:
        :return:
        """
        z = x.copy()
        z.update(y)
        return z

    def get_dict_from_properties(self, props, is_array="", required_list=None):
        if required_list is None:
            required_list = []
        ret_dict = {}
        for prop in props:
            ret_dict = self.merge_dicts(ret_dict,
                                        self.get_dict_from_each_property(props[prop], prop, is_array, required_list))
        return ret_dict

    def get_dict_from_each_property(self, prop, prop_name, is_array="", parent_required=None):
        """
        in case of a property with nested definitions return properties of each defination
        otherwise return property as a dictionary
        :param prop:
        :param prop_name:
        :param is_array:
        :param parent_required:
        :return:
        """
        if parent_required is None:
            parent_required = []
        prop_is_required = self.get_required(prop_name, parent_required)
        ret_dict = {}

        if prop is None:
            return ret_dict
        # if a definition is a combination of two or more definitions using $allOf
        if 'allOf' in prop:
            props = prop.get('allOf')
            temp_dict = {}
            for p in props:
                if '$ref' in p:
                    def_name = self.get_name_from_reference(p['$ref']) + is_array
                    if self.is_definition(def_name):
                        temp_dict = self.merge_dicts(temp_dict, self.get_definition_parameters(def_name))
                    elif self.is_parameter(def_name):
                        temp_dict = self.merge_dicts(temp_dict, self.get_parameters_from_reference(def_name))
                else:
                    required_list = p.get("required", [])
                    temp_dict = self.merge_dicts(temp_dict, self.filter_body_name_from_parameters(
                        self.get_dict_from_each_property(p, "body", is_array, parent_required=required_list)))
            ret_dict[prop_name + is_array] = (
            temp_dict, "Description for this property is currently not available.", prop_is_required)
        # if a property is referenced to another defination using $ref
        if '$ref' in prop:
            def_name = self.get_name_from_reference(prop['$ref']) + is_array
            if self.is_definition(def_name):
                if prop_name:
                    p_name = prop_name
                else:
                    p_name = self.remove_array_notation_from_name(self.get_variable_name_for_definition(def_name))
                def_desc = self.get_description_for_definition(def_name)
                tup = (def_name, def_desc, prop_is_required)
                ret_dict[p_name] = tup
            elif self.is_parameter(def_name):
                ret_dict = self.merge_dicts(ret_dict, self.get_parameters_from_reference(def_name))
        # if type is mentioned in propery for ex "type" : "object"
        elif 'type' in prop:
            # if type is interger,number,string or anything which is not a object or array
            if (prop['type'] != "object") and (prop['type'] != "array"):
                if "enum" in prop:
                    tup = (prop['type'] + is_array, self.get_description(prop),
                           prop_is_required, prop['enum'])
                else:
                    tup = (prop['type'] + is_array, self.get_description(prop), prop_is_required)
                ret_dict[prop_name] = tup

            # if "type":"object"
            elif prop['type'] == "object":
                prop_required_list = prop.get("required", [])
                ret_dict[prop_name + is_array] = (
                    self.get_dict_from_properties(prop.get("properties"), required_list=prop_required_list),
                    self.get_description(prop), prop_is_required)
            # if "type":"array"
            elif prop['type'] == "array":
                items = prop["items"]
                ret_dict = self.merge_dicts(ret_dict,
                                            self.get_dict_from_each_property(items, prop_name, is_array + "[]",
                                                                             prop_is_required))
            # if "type":"object_array"
            elif prop['type'] == "object_array":
                items = prop["items"]
                ret_dict = self.merge_dicts(ret_dict,
                                            self.get_dict_from_each_property(items, prop_name, is_array + "[]",
                                                                             prop_is_required))
        return ret_dict

    def get_type_dict_only(self, params):
        for p in params:
            if type(params[p][0]) is not dict:
                params[p] = params[p][0]
            else:
                params[p] = self.get_type_dict_only(params[p][0])
        return params

    def filter_body_name_from_parameters(self, params):
        """
        the body name is formatted according to java
        :param params:
        :return:
        """
        for param in params:
            if 'body' in param:
                if type(params.get(param)[0]) is dict:
                    return params.get(param)[0]
                elif self.is_definition(params.get(param)[0]):
                    new_params = {}
                    new_params[self.remove_array_notation_from_name(
                        params.get(param)[0][0].lower() + params.get(param)[0][1:])] = params.get(param)
                    return new_params
        return params

    def get_description_for_definition(self, p):
        """
        returns description from spec file for each definition
        :param p:
        :return:
        """
        description = ""
        for def_name, definition in list(self.parser.definitions().items()):
            if def_name.lower() in p.lower():
                if 'description' in definition:
                    description = definition.get("description", "")
                else:
                    description = "This is the default description for a definition"
                    description = ""
        return description

    def get_description(self, prop):
        """
        returns description of properties
        :param prop:
        :return:
        """
        if 'description' in prop:
            return prop['description']
        else:
            # return "This is the default description"
            return ""

    def get_required(self, prop_name, required):
        """
        returns if property is required
        :param prop_name:
        :param required:
        :return:
        """
        if isinstance(required, bool):
            return required
        if prop_name in required:
            return True
        else:
            return False

    def get_params_from_properties(self, props, param_type):
        """
        returns parameter and their description
        :param props:
        :param param_type:
        :return:
        """
        required_params = {}
        required_params_desc = {}
        if 'parameters' in props:
            params = props.get("parameters")
            for param in params:
                if '$ref' in param:
                    pn = self.get_name_from_reference(param.get("$ref"))
                    for param_name, parameters in list(self.parser.parameters().items()):
                        if (param_name == pn) and (parameters.get("in") == param_type):
                            required_params[parameters.get("name")] = parameters.get("type").title()
                            required_params_desc[parameters.get("name")] = parameters.get("description", "")
                if ('in' in param) and (param.get("in") == param_type):
                    required_params[param.get("name")] = param.get("type").title()
                    required_params_desc[param.get("name")] = param.get("description", "")
        return required_params, required_params_desc

    def is_definition(self, p):
        """
        returns true if definition
        :param p:
        :return:
        """

        for def_name, definition in list(self.parser.definitions().items()):
            if def_name == self.remove_array_notation_from_name(p):
                return True
        return False

    def is_parameter(self, p):
        """
        returns true if parameter
        :param p:
        :return:
        """
        for param_name, params in list(self.parser.parameters().items()):
            if param_name == self.remove_array_notation_from_name(p):
                return True
        return False

    def check_if_request_is_single_model(self, req_parameters):
        """
        checks if request is a definition
        :param req_parameters:
        :return:
        """
        if len(req_parameters) == 1:
            for rp in req_parameters:
                if (type(req_parameters[rp][0]) is not dict) and (
                self.is_definition(self.remove_array_notation_from_name(req_parameters[rp][0]))):
                    return True
        return False

    def get_model_name_from_parameter(self, req_parameters):

        for rp in req_parameters:
            return self.remove_array_notation_from_name(req_parameters[rp][0])

    def filter_single_type_array(self, parameters):

        if (len(parameters) == 1) and ('body' in parameters):
            return {}, parameters['body']
        return parameters, ''
