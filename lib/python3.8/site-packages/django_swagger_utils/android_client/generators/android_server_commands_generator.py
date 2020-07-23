from django_swagger_utils.android_client.generators.android_generator import AndroidGenerator
import os
import collections
from io import open

class AndroidServerCommandsGenerator(AndroidGenerator):
    #   TODO : Only "POST" and "GET" methods are supported as of now. Add functionality for others later.
    def __init__(self, app_name, parser, paths, base_path):
        AndroidGenerator.__init__(self, app_name, parser, paths, base_path)
        self.parser = parser
        self.paths = paths
        self.base_path = base_path

    def generate_android_server_commands(self):
        """
        generates the java code of ServerCommands interface file
        the file is created in network folder

        :return:
        """
        f = open(self.base_path + "/network/" + self.snake_to_camel_case(self.app_name) + "ServerCommands.java", "w")
        f.write("package " + self.get_import_statement_from_path(self.base_path) + ".network;\n")
        #imports all requests and responses
        for path_name, path in list(self.parser.paths().items()):
            for method, method_props in list(path.items()):
                if (method == "post") or (method == "get") or (method == "delete") or (method == "put"):
                    op = self.snake_to_camel_case(method_props.get('operationId'))
                    if os.path.exists(self.base_path + "/models/requests/" + op + "/"):
                        f.write("import " + self.get_import_statement_from_path(
                            self.base_path) + ".models.requests." + op + ".*;\n")
                    if os.path.exists(self.base_path + "/models/responses/" + op + "/"):
                        f.write("import " + self.get_import_statement_from_path(
                            self.base_path) + ".models.responses." + op + ".*;\n")

        f.write("import " + self.get_import_statement_from_path(self.base_path + "/models/common") + ".*;\n")
        f.write("import retrofit.http.Body;\n")
        f.write("import retrofit.http.Path;\n")
        f.write("import retrofit.http.Query;\n")
        f.write("import retrofit.http.POST;\n")
        f.write("import retrofit.http.GET;\n")
        f.write("import retrofit.http.PUT;\n")
        f.write("import retrofit.http.DELETE;\n\n")
        f.write("import java.util.ArrayList;\n\n")
        f.write("public interface " + self.snake_to_camel_case(self.app_name) + "ServerCommands {\n\n")
        #iterates through all the paths in the spec file
        for path_name, path in list(self.parser.paths().items()):
            path_params = {}
            query_params = {}
            path_params = self.get_params_from_properties(path, "path")[0]
            query_params = self.get_params_from_properties(path, "query")[0]
            #iterates through all methods of a path
            for method, method_props in list(path.items()):
                if (method == "post") or (method == "get") or (method == "delete") or (method == "put"):
                    op = self.snake_to_camel_case(method_props.get("operationId"))
                    op_lower = op[0].lower() + op[1:]
                    path_method_params = self.merge_dicts(path_params,
                                                          self.get_params_from_properties(method_props, "path")[0])
                    path_method_params = collections.OrderedDict(sorted(path_method_params.items()))
                    query_method_params = self.merge_dicts(query_params,
                                                           self.get_params_from_properties(method_props, "query")[0])
                    query_method_params = collections.OrderedDict(sorted(query_method_params.items()))

                    req_parameters = self.get_request_parameters(path)
                    req_parameters = self.merge_dicts(req_parameters, self.get_request_parameters(method_props))
                    res_parameters = self.get_response_parameters(method_props)
                    req_parameters = collections.OrderedDict(list(req_parameters.items()))
                    res_parameters = collections.OrderedDict(list(res_parameters.items()))

                    req_is_array = ""

                    if self.check_if_request_is_array(req_parameters):
                        req_is_array = "[]"

                    res_is_array = ""
                    if self.check_if_response_is_array(method_props):
                        res_is_array = "[]"

                    req_is_single_model = self.check_if_request_is_single_model(req_parameters)
                    android_model = ""
                    if req_is_single_model:
                        android_model = self.get_model_name_from_parameter(req_parameters)
                        android_model = android_model[0].upper() + android_model[1:]

                    res_is_single_model = self.check_if_request_is_single_model(res_parameters)
                    android_res_model = ""
                    if res_is_single_model:
                        android_res_model = self.get_model_name_from_parameter(res_parameters)

                    req_parameters, req_is_single_type_array = self.filter_single_type_array(req_parameters)
                    res_parameters, res_is_single_type_array = self.filter_single_type_array(res_parameters)

                    response_content = ""
                    if res_parameters:
                        if not res_is_single_model:
                            response_content = op + "Response"
                        else:
                            response_content = android_res_model[0].upper() + android_res_model[1:]
                    else:
                        if res_is_single_type_array:
                            res_is_array = ""
                            response_content = res_is_single_type_array[0].capitalize()
                        else:
                            response_content = "Void"

                    body_content = ""
                    #executes if api has request parameter
                    if req_parameters:
                        if not req_is_single_model:
                            body_content = "@Body " + op + "Request" + req_is_array + " " + op_lower + "Request"
                        else:
                            body_content = "@Body " + android_model + req_is_array + " " + android_model.lower()
                    elif req_is_single_type_array:

                        body_content = "@Body " + req_is_single_type_array[0].capitalize() + " " + op_lower + "Request"
                    if (path_method_params or query_method_params) and body_content:
                        body_content = body_content + ", "

                    # url_prefix = "/api/" + self.app_name
                    url_prefix = self.parser.api_base_path()
                    url_prefix = url_prefix[:-1]
                    f.write("\t@" + method.upper() + '("' + url_prefix + path_name + '")' + "\n")
                    f.write("\t" + response_content + res_is_array + " " + op_lower + "(" + body_content)
                    #executes if method has path parameters
                    if path_method_params:
                        path_params_len = len(path_method_params)
                        counter = 0
                        for pp in path_method_params:
                            f.write('@Path("' + pp + '") ' + self.get_corresponding_java_data_type(
                                path_method_params[pp].lower()) + " " + pp)
                            if counter != path_params_len - 1:
                                f.write(",")
                            elif counter == path_params_len - 1:
                                if query_method_params:
                                    f.write(", ")
                            counter += 1
                    #executes if method as query parameters
                    if query_method_params:
                        query_params_len = len(query_method_params)
                        counter = 0
                        # iterates through all query parmeters
                        for qp in query_method_params:
                            f.write('@Query("' + qp + '") ' + self.get_corresponding_java_data_type(
                                query_method_params[qp].lower()) + " " + qp)
                            if counter != query_params_len - 1:
                                f.write(", ")
                            counter += 1
                    f.write(");\n\n")
        f.write("}")
        f.close()
