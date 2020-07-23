import json
import os

from .conf import render


class URLGenerator(object):
    context_properties = None

    def __init__(self, app_name, dir_paths, parser):
        self.app_name = app_name
        self.dir_paths = dir_paths
        self.parser = parser

    def configure(self):
        self.set_context_properties()

    def set_context_properties(self):
        self.context_properties = self.get_url_context_properties()

    def get_tagged_context_properties(self):
        tagged_props = {}
        for path, props in list(self.context_properties.items()):
            for tag in props.get('tags', []):
                try:
                    tagged_props[tag][path] = props
                except KeyError:
                    tagged_props[tag] = {path: props}
        return tagged_props

    def generate_url(self):
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        from django_swagger_utils.core.utils.case_convertion import (
            hyphen_to_camel, camel_to_snake)
        url_file_contents = self.get_url_file_contents(self.context_properties)
        url_path = self.dir_paths["url_file"]

        write_to_file(url_file_contents, url_path)

        for tag, props in list(self.get_tagged_context_properties().items()):
            tag_url_file_contents = self.get_url_file_contents(props)

            tag_url_path = os.path.join(
                os.path.dirname(self.dir_paths["url_file"]), "url_groups",
                "{}.py".format(camel_to_snake(hyphen_to_camel(tag))))
            write_to_file(tag_url_file_contents, tag_url_path)

    def generate_view_environment(self):

        for url_path, path_properties in list(self.context_properties.items()):
            path_method_dict_str = json.dumps(
                path_properties["path_method_dict"], indent=4)
            context_properties = {
                "path_method_dict_str": path_method_dict_str,
                "path_method_name": path_properties["view_environment"][
                    "path_name"],
                "app_name": self.app_name
            }
            view_environment_file_contents = self.get_view_environment_router_file_contents(
                context_properties)
            view_environment_file_path = path_properties["view_environment"][
                "view_environment_router_path"]

            from django_swagger_utils.core.utils.write_to_file import \
                write_to_file
            write_to_file(view_environment_file_contents,
                          view_environment_file_path)

    def get_url_context_properties(self):
        context_properties = {}
        all_method_operation_ids = []
        for path_name, path in list(self.parser.paths().items()):
            from django_swagger_utils.drf_server.generators.path_generator import \
                PathGenerator

            tags = []
            group_name = ''
            for method, value in list(path.items()):
                if method in ('get', 'post', 'put', 'delete'):
                    for tag in value.get('tags', []):
                        tags.append(tag)
                    if value.get('x-group'):
                        group_name = value.get('x-group')

            path_generator = PathGenerator(self.app_name, self.dir_paths, path,
                                           path_name, self.parser, group_name)
            path_method_dict, view_environment_path_dict, operation_ids = path_generator.get_urls()
            all_method_operation_ids.extend(operation_ids)

            context_properties[path_name] = {
                "path_method_dict": path_method_dict,
                "view_environment": view_environment_path_dict,
                "tags": tags
            }

        return context_properties

    @staticmethod
    def get_url_file_contents(context_properties):
        return render('urls.j2', {"path_names": context_properties})

    @staticmethod
    def get_view_environment_router_file_contents(context_properties):
        return render('router.j2', context_properties)
