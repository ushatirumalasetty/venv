# coding=utf-8
import os
from io import open


class MkDirs(object):

    def mk_dir_if_not_exits(self, file_name, init_required = True):
        """
        creates directory for a given file
        :param file_name:
        :param init_required:
        :return:
        """
        file_directory = os.path.dirname(file_name)
        self.mk_dir_recursive(file_directory + "/", init_required)

    def mk_dir_recursive(self, path, init_required):
        """
        cretes directory and init file if required
        :param path:
        :param init_required:
        :return:
        """
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self.mk_dir_recursive(sub_path, init_required)
            if init_required:
                init_file = open(os.path.join(sub_path, '__init__.py'), "w+")
                init_file.close()
        if not os.path.exists(path):
            os.mkdir(path)
