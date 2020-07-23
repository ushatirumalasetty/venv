import json
import jsonpatch
import shutil
import os
from io import open


class PatchGenerator(object):
    def __init__(self, app_name, parser, paths, base_path):
        self.app_name = app_name
        self.parser = parser
        self.base_path = base_path
        self.paths = paths
        self.src_path = self.paths["api_specs_json"]
        self.des_path = os.path.join(self.paths["api_spec_migrations_dir"], "api_spec.json")
        self.des_dir = self.paths["api_spec_migrations_dir"]
        self.op_of_last_version = []

        from django_swagger_utils.core.utils.mk_dirs import MkDirs
        MkDirs().mk_dir_if_not_exits(file_name=self.des_path)

    def generate_json_patch(self):
        '''
        the patches and a copy of spec file are saved at migrations dir
        this is executed prior to jar generation and document generation
        if its the first time only a spec file is saved
        other wise corresponding changes are saved in form of .json patch file
        :return:
        '''

        with open(self.src_path) as src_json:
            src = json.load(src_json)
        if os.path.exists(self.des_path):

            with open(self.des_path) as des_json:

                des = json.load(des_json)

                final_des = self.apply_all_patches(des)

                if final_des != src:
                    patch = jsonpatch.make_patch(final_des, src)

                    self.store_patch(patch)

        else:

            shutil.copyfile(self.src_path, self.des_path)

    def apply_all_patches(self, dest):
        '''
        this records applies all the patches
        :param dest: api_spec.json
        :return: a path,version number and list of versions
        '''

        final_dest = dest

        dir_list = os.listdir(self.des_dir)
        version_list = []

        for dl in dir_list:
            if '_patch.json' in dl:
                version_num = int(dl.replace("_patch.json", ""))
                version_list.append(version_num)
        version_list.sort(reverse=False)

        from django.conf import settings

        version_split = getattr(settings, 'MAX_APIDOC_VERSIONS', len(version_list))
        version_list2 = []
        if len(version_list) >= version_split:
            version_list2 = version_list[len(version_list) - version_split:]
        i = 0
        version = 0

        if len(version_list) != 0:
            for vnum in version_list:

                with open(os.path.join(self.des_dir, str(vnum).zfill(4) + "_patch.json"), "r") as dest_patch_file:

                    patch_string = dest_patch_file.read().replace('\n', '')

                    patch = jsonpatch.JsonPatch.from_string(str(patch_string))
                    final_dest = patch.apply(final_dest)

                if version_list2:
                    if vnum == version_list2[i]:
                        i = i + 1

            return final_dest
        else:
            return final_dest

    def generate_docs(self, vnum, patch_json_dict):
        '''
        an intermediate function ,passes control to fucnction that generates .py files with api specification
        :param vnum: version number
        :param patch_json_dict: spec file
        :return:
        '''
        from django_swagger_utils.core.parsers.swagger_parser import SwaggerParser
        patch_parser = SwaggerParser(patch_json_dict)
        from django_swagger_utils.apidoc_gen.generators.api_doc_generator import ApiDocGenerator
        api_doc_generator = ApiDocGenerator(self.app_name, patch_parser, self.paths, self.base_path)
        api_doc_generator.generate_docs(vnum, self.op_of_last_version)

    def store_patch(self, patch):
        '''
        saves the patch in the migrations directory
        :param patch:
        :return:
        '''
        import os

        dir_list = os.listdir(self.des_dir)
        version_list = []
        for dl in dir_list:
            if '_patch.json' in dl:
                version_num = int(dl.replace("_patch.json", ""))
                version_list.append(version_num)
        version_list.sort(reverse=True)
        if len(version_list) == 0:
            initial_patch = os.path.join(self.des_dir, '0001_patch.json')
            with open(initial_patch, 'w') as dest_patch_file:
                dest_patch_file.write(json.dumps(json.loads(str(patch)), indent=4))
        else:
            version_num = version_list[0] + 1
            version_patch = os.path.join(self.des_dir, str(version_num).zfill(4) + "_patch.json")
            with open(version_patch, 'w') as dest_patch_file:
                dest_patch_file.write(json.dumps(json.loads(str(patch)), indent=4))
        return version_list

    def filter_for_deleted_apis(self):
        '''


        :param version_list: a list of versions
        :return:
        '''
        with open(self.src_path) as src_json:
            src = json.load(src_json)
        if os.path.exists(self.des_path):

            with open(self.des_path) as des_json:
                des = json.load(des_json)
                final_dest = des
            for path_name, path in list(self.parser.paths().items()):

                for method, method_props in list(path.items()):
                    # Handle common parameters later

                    if (method == 'get') or (method == 'post') or (method == 'delete') or (method == 'put'):
                        operation_id = method_props.get("operationId")
                        self.op_of_last_version.append(operation_id)

            self.generate_docs(1, des)
            from django.conf import settings

            version_number = 1
            patch_list = []
            for file in os.listdir(self.des_dir):
                if "_patch.json" in file:
                    patch_list.append(file)

            if len(patch_list) != 0:
                for patch in sorted(patch_list):
                    version_number += 1

                    with open(os.path.join(self.des_dir, patch), "r") as dest_patch_file:

                        patch_string = dest_patch_file.read().replace('\n', '')

                        patch = jsonpatch.JsonPatch.from_string(str(patch_string))
                        final_dest = patch.apply(final_dest)
                    if version_number == len(patch_list) + 1:
                        for path_name, path in list(self.parser.paths().items()):

                            for method, method_props in list(path.items()):
                                # Handle common parameters later

                                if (method == 'get') or (method == 'post') or (method == 'delete') or (method == 'put'):
                                    operation_id = method_props.get("operationId")
                                    self.op_of_last_version.append(operation_id)

                    self.generate_docs(version_number, final_dest)


        else:
            for path_name, path in list(self.parser.paths().items()):

                for method, method_props in list(path.items()):
                    # Handle common parameters later

                    if (method == 'get') or (method == 'post') or (method == 'delete') or (method == 'put'):
                        operation_id = method_props.get("operationId")
                        self.op_of_last_version.append(operation_id)

            self.generate_docs(1, src)
