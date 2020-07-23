import importlib

from .conf import render


class RequestResponseGenerator(object):
    security_definitions_import_strs = []

    def __init__(self, security_definitions, consumes, produces, security,
                 paths):
        self.security_definitions = security_definitions
        self.consumes = consumes
        self.produces = produces
        self.security = security
        self.paths = paths

    def options_str(self):
        return render('request_response.j2', {
            'consumes': self.consumes, 'produces': self.produces,
            'securities': self.security
        })

    def security_definitions_str(self):
        security_definitions = [self.get_security_definitions_obj(security_name, security)
                                for security_name, security in list(self.security_definitions.items())]
        return render('security_definitions.j2', {
            'security_definitions': security_definitions,
            'import_strs': list(set(self.security_definitions_import_strs))
        })

    def get_api_key_authentication_class(self):
        from django.conf import settings
        auth_class_name = getattr(settings, 'API_KEY_AUTHENTICATION_CLASS', '')
        if auth_class_name:
            try:
                getattr(importlib.import_module(
                    ".".join(auth_class_name.split(".")[:-1])),
                    auth_class_name.split(".")[-1]
                )
                import_str = "from %s import %s" % (
                    ".".join(auth_class_name.split(".")[:-1]),
                    auth_class_name.split(".")[-1]
                )
                self.security_definitions_import_strs.append(import_str)
                return [auth_class_name.split(".")[-1]]
            except ImportError:
                raise
        return []
    def get_security_definitions_obj(self, security_name, security):
        security_obj = {
            "SECURITY_NAME": security_name
        }
        if security["type"] == "basic":
            security_obj["TYPE"] = "BASIC"
            security_obj["AUTHENTICATION_CLASSES"] = ["BasicAuthentication"]
            security_obj["PERMISSIONS_REQUIRED"] = ["IsAuthenticated"]
            security_obj["SCOPES_REQUIRED"] = []
        elif security["type"] == "apiKey":
            security_obj["TYPE"] = "API_KEY"

            security_obj["AUTHENTICATION_CLASSES"] = \
                self.get_api_key_authentication_class()
            security_obj["PERMISSIONS_REQUIRED"] = [
                self.get_api_key_permission_str(security)]
            security_obj["SCOPES_REQUIRED"] = []
        else:
            security_obj["TYPE"] = "OAUTH2"
            security_obj["AUTHENTICATION_CLASSES"] = ["OAuth2Authentication"]
            security_obj["PERMISSIONS_REQUIRED"] = ["IsAuthenticated"]
            security_obj["SCOPES_REQUIRED"] = ["\"%s\"" % scope for scope in list(security["scopes"].keys())]
        return security_obj

    @staticmethod
    def get_api_key_permission_str(security):
        name = security["name"]
        permission_name = name.replace("-", "").upper() + "Permission"
        header = "True" if security["in"] == "header" else "False"
        api_key_permission = "IsValidAPIKey(\"%s\", {\"name\": \"%s\", \"is_header\": %s})" % (permission_name, name,
                                                                                               header)
        return api_key_permission

    def generate_request_response_options_file(self):
        options_str = self.options_str()
        decorator_options_file_path = self.paths["decorator_options_file"]

        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(options_str, decorator_options_file_path)
        return options_str

    def generate_security_definitions_file(self):
        security_definitions_str = self.security_definitions_str()
        security_definitions_file_path = self.paths["security_definitions_file"]

        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(security_definitions_str, security_definitions_file_path)
        return security_definitions_str

    def generate_request_response_package(self):

        # create request response decorator options file
        self.generate_request_response_options_file()

        # create decorator definitions file
        self.generate_security_definitions_file()
