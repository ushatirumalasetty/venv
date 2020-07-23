import json
from io import open

from django_swagger_utils.core.generators.generator import Generator
from django_swagger_utils.core.generators.swagger_sample_schema import \
    SwaggerSampleSchema


class ApiDocGenerator(Generator):
    def __init__(self, app_name, parser, paths, base_path):
        Generator.__init__(self, app_name, parser, paths, base_path)

    def generate_docs(self, version, apis_of_last_version):
        '''
        generates  python file with api details according to apidoc syntax
        :param version: the version number
        :param apis_of_last_version: a list with only the apis present in the last version
        :return:
        '''
        from django_swagger_utils.core.utils.mk_dirs import MkDirs
        # making directory for the first time
        MkDirs().mk_dir_if_not_exits(file_name=self.base_path)
        # creating or opening a .py file
        f = open(self.base_path + "/v0.0." + str(version) + ".py", "w")
        definitions = self.parser.definitions()
        # traversing through all paths
        for path_name, path in list(self.parser.paths().items()):
            path_params = {}
            query_params = {}
            path_params_desc = {}
            query_params_desc = {}
            req_header_params = {}
            req_header_params_desc = {}
            req_parameters = {}
            res_header_params = {}
            res_header_params_desc = {}
            path_params, path_params_desc = self.get_params_from_properties(
                path, "path")
            query_params, query_params_desc = self.get_params_from_properties(
                path, "query")
            req_parameters = self.get_request_parameters(path)
            # traversing through all methods
            for method, method_props in list(path.items()):

                # Handle common parameters later

                if (method == 'get') or (method == 'post') or (
                    method == 'delete') or (method == 'put'):
                    path_method_params = self.merge_dicts(path_params,
                                                          self.get_params_from_properties(
                                                              method_props,
                                                              "path")[0])
                    path_method_params_desc = self.merge_dicts(
                        path_params_desc,
                        self.get_params_from_properties(method_props, "path")[
                            1])
                    query_method_params = self.merge_dicts(query_params,
                                                           self.get_params_from_properties(
                                                               method_props,
                                                               "query")[0])
                    query_method_params_desc = self.merge_dicts(
                        query_params_desc,
                        self.get_params_from_properties(method_props, "query")[
                            1])
                    req_header_params, req_header_params_desc = self.get_request_headers(
                        method_props, path)
                    res_header_params, res_header_params_desc = self.get_response_headers(
                        method_props)
                    operation_id = method_props.get("operationId")
                    if operation_id in apis_of_last_version:
                        modified_path_name = self.get_final_path_name(
                            path_name, query_method_params)
                        f.write('"""')
                        f.write("\n")

                        f.write(
                            "@api {" + method + "} " + "/api/" + self.app_name + modified_path_name + " " +
                            operation_id + "\n")

                        # gets the group or tag of api
                        f.write("@apiGroup " + self.app_name + " APP")
                        tags = method_props.get("tags")
                        if tags:
                            for tag in tags:
                                f.write(" " + tag)

                        f.write("\n")
                        # gets the version the patch
                        f.write("@apiVersion 0.0." + str(version) + "\n")

                        description = method_props.get("description", '')
                        group = method_props.get("group")
                        deprecated = method_props.get("deprecated")

                        if description:
                            description = "<b>Description:</b> {}<br />".format(
                                description)
                        description += self.get_content_string_for_api_description(
                            method_props=method_props)
                        if description:
                            # prints description if present
                            f.write("@apiDescription " + description + "\n")
                            # f.write("@apiDefine "+operation_id+" "+description+"\n")
                        if str(deprecated) == "True":
                            # prints if api is deprecated (only if true)
                            f.write("@apiDeprecated " + str(deprecated))

                        self.print_examples_for_req_schema(definitions,
                                                           method_props, f)
                        self.print_examples_for_res_schema(definitions,
                                                           method_props, f)

                        req_method_parameters = self.merge_dicts(
                            req_parameters,
                            self.get_request_parameters(method_props))
                        res_method_parameters = self.get_response_parameters(
                            method_props)
                        f.write("\n")
                        if self.check_if_request_is_single_model(
                            req_method_parameters):
                            android_model = self.get_model_name_from_parameter(
                                req_method_parameters)
                            self.print_api("Param",
                                           self.get_definition_parameters(
                                               android_model), f)
                        else:
                            self.print_api("Param", req_method_parameters, f)
                        self.print_required_params("Param", "PathParameter",
                                                   path_method_params,
                                                   path_method_params_desc, f)
                        self.print_required_params("Param", "QueryParameter",
                                                   query_method_params,
                                                   query_method_params_desc,
                                                   f)
                        f.write("\n")
                        # self.print_required_params("Header", "RequestHeader", req_header_params, req_header_params_desc,
                        #                            f)
                        # f.write("\n")
                        # self.print_required_params("Header", "ResponseHeader", res_header_params,
                        #                            res_header_params_desc, f)
                        # f.write("\n")
                        self.print_required_params_example(path_method_params,
                                                           f)

                        if self.check_if_request_is_single_model(
                            res_method_parameters):
                            android_model = self.get_model_name_from_parameter(
                                res_method_parameters)
                            self.print_api("Success",
                                           self.get_definition_parameters(
                                               android_model), f)
                        else:
                            self.print_api("Success", res_method_parameters, f)

                        flag = 0
                        for res_type in method_props.get("responses"):
                            if (str(res_type) != '200') and (
                                str(res_type) != 'default'):
                                response = method_props.get("responses").get(
                                    res_type)
                                response_description = response.get(
                                    "description")
                                schema, response_description = self.get_error_response_schema(
                                    response,
                                    response_description)
                                # prints if error is specified                                                      response_description)
                                f.write("@apiError %s %s\n" % (
                                    str(res_type), response_description))
                                if schema:
                                    if flag == 0:
                                        f.write(
                                            "@apiErrorExample {json} Error-Response : \n")
                                        flag = 1
                                    f.write("\tHTTP/1.1 " + res_type + " \n")
                                    swagger_sample = SwaggerSampleSchema(
                                        definitions, schema)
                                    example_dict = swagger_sample.get_data_dict()
                                    f.write(json.dumps(example_dict,
                                                       indent=4) + "\n")
                                    f.write("\n")

                        f.write("\n")
                        f.write('"""')
                        f.write("\n")
                    else:
                        pass

        self.get_content_string_for(f, "0.0.{}".format(version), self.app_name)
        f.close()

    def get_content_string_for(self, f, version, app_name):
        content = """
@api / 
@apiGroup Jira
@apiVersion {}
@apiName LinkedIssues 
@apiDescription
<ul>
{}
</ul>  

"""
        links = []
        for link in self.parser.sepc_json.get('x-issue-links', []):
            list_item = \
                "<li><a href={}>{}</a></li>".format(
                    link, self._get_issue_id_from_link(link)
                )

            links.append(list_item)
        if not links:
            return
        links.reverse()
        content = content.format(version, "".join(links))
        f.write('"""')
        f.write(content)
        f.write('"""')

    @staticmethod
    def _get_issue_id_from_link(link):
        link = link.strip(' ')
        link = link.strip('/')
        return link.split('/')[-1]

    def get_content_string_for_api_description(self, method_props):
        content = """
        <br />
        <b> Linked Issues</b>: <br />
        <ul>
        {}
        </ul>
        <br />  
        """
        links = []
        for link in method_props.get('x-issue-links', []):
            list_item = \
                "<li><a href={}>{}</a></li>".format(
                    link, self._get_issue_id_from_link(link)
                )

            links.append(list_item)
        links.reverse()
        if not links:
            return ''
        content = content.format("<br/>".join(links))
        return content

    def print_required_params_example(self, params, f):
        '''
        prints path parameter example in json format (only if present)
       :param params:list of path parameters
       :param f:file object
       :return:
       '''

        if len(params) == 0:
            return
        f.write("@apiExample {json} ExamplePathParameters:\n")

        dict = {}

        for param in params:
            plain_dict = {
                param: "integer"
            }
            dict.update(plain_dict)
        f.write(json.dumps(dict, indent=4) + "\n")
        # swagger_sample = SwaggerSampleSchema(definitions, param.get("schema"))

        # example_dict = swagger_sample.get_data_dict()
        # f.write(json.dumps(example_dict, indent=4) + "\n")

    # f.write("{\t"+)

    def print_api(self, api_type, res_params, f, parent=""):
        '''
        prints apis
        :param api_type: type of operation (get,post etc)
        :param res_params: the response parameters
        :param f: file object
        :return:
        '''
        if res_params is not None:
            for rp in res_params:
                if type(res_params[rp][0]) is not dict:
                    rp_str = rp
                    rp_type = res_params[rp][0][0].capitalize() + \
                              res_params[rp][0][1:]
                    if not res_params[rp][2]:
                        rp_str = "[%s]" % rp_str

                    description = res_params[rp][1]
                    if len(res_params[rp]) == 4:
                        enums_list = res_params[rp][3]
                        str_list = "".join([
                            "<li>{}</li>".format(enum_item)
                            for enum_item in enums_list
                        ])
                        if str_list:
                            enums_str = """
                            <ul>
                            {}
                            </ul>
                            """.format(str_list)
                            description += enums_str
                    f.write(
                        "@api" + api_type + self.remove_array_notation_from_name(
                            parent) + " {" + rp_type + "} " + rp_str + " " + str(
                            description))

                    f.write("\n")
                    if self.is_definition(res_params[rp][0]):
                        # TODO: ADD = FOR DEFAULT VALUES , "small","huge"
                        # TODO: ADD RANGE FOR {DATA TYPE}
                        self.print_api(api_type,
                                       self.get_definition_parameters(
                                           res_params[rp][0]), f,
                                       " (" + res_params[rp][0] + ")")
                else:
                    rp_str = self.remove_array_notation_from_name(rp)
                    if not res_params[rp][2]:
                        rp_str = "[%s]" % rp_str
                    f.write(
                        "@api" + api_type + self.remove_array_notation_from_name(
                            parent) +
                        " {" + self.snake_to_camel_case(rp) + "} " +
                        rp_str + " " +
                        str(res_params[rp][1]))
                    f.write("\n")
                    self.print_api(api_type, res_params[rp][0], f,
                                   " (" + self.snake_to_camel_case(rp) + ")")

    def print_required_params(self, api_type, params_type, params, params_desc,
                              f):
        '''
        prints parameters
        :param api_type: type of operation (get,post etc)
        :param params_type: type of parameters (query,path etc)
        :param params: list of  parameters
        :param params_desc: description of parameters
        :param f: file object
        :return:
        '''
        for param in params:
            '''
        prints parameters 
        :param api_type: type of operation (get,post etc)
        :param params_type: type of parameters (query,path etc)
        :param params: list of  parameters
        :param params_desc: description of parameters
        :param f: file object
        :return:
        '''
            f.write("@api" + api_type + " (" + params_type + ") {" + params[
                param] + "} " + param + " " + params_desc[
                        param] + "\n")

    def print_examples_for_req_schema(self, definitions, method_props, f):
        '''
        prints examples for requested schema in json
        :param definitions: definitions object
        :param method_props: properties of method object
        :param f: file object
        :return:
        '''
        if 'parameters' in method_props:
            parameters = method_props.get("parameters")
            for params in parameters:
                if '$ref' in params:
                    param = self.get_name_from_reference(params.get("$ref"))
                    for param_name, params_ref in list(
                        self.parser.parameters().items()):
                        if (param_name == param) and (
                            params_ref.get('in') == "body"):
                            swagger_sample = SwaggerSampleSchema(definitions,
                                                                 params_ref.get(
                                                                     "schema"))
                            example_dict = swagger_sample.get_data_dict()
                            f.write("@apiExample {json} ExampleRequest:\n")
                            f.write(json.dumps(example_dict, indent=4) + "\n")
                if params.get("in") == "body":
                    swagger_sample = SwaggerSampleSchema(definitions,
                                                         params.get("schema"))
                    example_dict = swagger_sample.get_data_dict()
                    f.write("@apiExample {json} ExampleRequest:\n")
                    f.write(json.dumps(example_dict, indent=4) + "\n")

    def print_examples_for_res_schema(self, definitions, method_props, f):
        '''
        prints examples for success response schema in json
        :param definitions: definitions object
        :param method_props: properties of method object
        :param f: file object
        :return:
        '''
        # TODO : Referenced parameters are not getting printed. Do them later.
        if "200" in method_props.get("responses"):
            response = method_props.get("responses").get("200").get("schema")
            response1 = method_props.get("responses").get("200").get('$ref')
            description = method_props.get("responses").get("200").get(
                'description')
            if response:
                swagger_sample = SwaggerSampleSchema(definitions, response)
                example_dict = swagger_sample.get_data_dict()
                f.write("@apiExample {json} ExampleResponse:\n")
                f.write(json.dumps(example_dict, indent=4) + "\n")
            if response1:
                api_name = self.get_name_from_reference(response1)
                for res_name, res_ref in list(self.parser.responses().items()):
                    if (api_name == res_name):
                        swagger_sample = SwaggerSampleSchema(definitions,
                                                             res_ref.get(
                                                                 "schema"))
                        example_dict = swagger_sample.get_data_dict()
                        f.write("@apiExample {json} ExampleResponse:\n")
                        f.write(json.dumps(example_dict, indent=4) + "\n")

    @staticmethod
    def get_final_path_name(path_name, query_parameters):
        '''
       returns path address
       :param path_name: path name
       :param query_parameters: query parameters list
       :return path: path
       '''

        path = path_name
        if query_parameters:
            path = path + "?"
        for qp in query_parameters:
            path = path + qp + "=?&"
        return path

    def get_response_headers(self, method_props):
        '''
        prints response heders in json
        :param method_props: properties of method object
        :return res_headers:response headers
        :return res_headers_desc:response headers description
        '''
        res_headers = {}
        res_headers_desc = {}
        res_headers['Accept'] = 'String'
        if 'produces' not in method_props:
            accept = ''
            for p in self.parser.produces():
                accept = accept + p + ", "
        else:
            accept = ''
            for p in method_props.get("produces"):
                accept = accept + p + ", "
        res_headers_desc['Accept'] = accept
        if '200' in method_props.get("responses"):
            if 'headers' in method_props.get("responses").get("200"):
                headers = method_props.get("responses").get("200").get(
                    "headers")
                for h in headers:
                    res_headers[h] = headers[h]['type']
                    res_headers_desc[h] = headers[h].get('description', "")
            elif '$ref' in method_props.get("responses").get("200"):
                res = self.get_name_from_reference(
                    method_props.get("responses").get("200").get("$ref"))
                for res_name, resp in list(self.parser.responses().items()):
                    if (res == res_name) and ('headers' in resp):
                        headers = resp.get("headers")
                        for h in headers:
                            res_headers[h] = headers[h]['type']
                            res_headers_desc[h] = headers[h]['description']
        return res_headers, res_headers_desc

    def get_request_headers(self, method_props, path):
        '''
        prints request heders in json
        :param method_props: properties of method object
        :param path:path
        :return res_headers:response headers
        :return res_headers_desc:response headers description
        '''
        req_headers = {}
        req_headers_desc = {}
        req_headers['Content-type'] = 'String'
        if 'consumes' not in method_props:
            cont_type = ', '.join(self.parser.consumes())
        else:
            cont_type = ', '.join(method_props.get("consumes"))

        req_headers_desc['Content-type'] = cont_type
        req_headers = self.merge_dicts(req_headers,
                                       self.get_params_from_properties(path,
                                                                       "header")[
                                           0])
        req_headers = self.merge_dicts(req_headers,
                                       self.get_params_from_properties(
                                           method_props, "header")[0])
        req_headers_desc = self.merge_dicts(req_headers_desc,
                                            self.get_params_from_properties(
                                                path, "header")[1])
        req_headers_desc = self.merge_dicts(req_headers_desc,
                                            self.get_params_from_properties(
                                                method_props, "header")[1])
        return req_headers, req_headers_desc

    def get_error_response_schema(self, response, response_description):
        '''
        prints error response if any in json
        :param response: response code
        :param response_description:error description
        :return schema:json schema
        :return response_description:error description

        '''
        schema = None
        if 'schema' in response:
            schema = response.get("schema")
        elif '$ref' in response:
            res = self.get_name_from_reference(response.get("$ref"))
            for res_name, resp in list(self.parser.responses().items()):
                if res == res_name:
                    response_description = resp.get("description")
                    schema = resp.get("schema")
                    break
        return schema, response_description
