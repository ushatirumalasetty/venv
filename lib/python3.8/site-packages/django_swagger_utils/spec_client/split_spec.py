import glob
import os
from io import open


class SplitSpec(object):
    """
    class is used to split the current spec file(api_spec.json)
    """

    def __init__(self, api_dir, base_dir):
        self.api_dir = api_dir
        self.base_dir = base_dir

    def remove_yaml_files(self, path='./specs'):
        """
        this method is basically being used to remove all the unnecessary .yaml files
        from the /specs directory after the yaml files have been converted json files
        :param path:
        :return:
        """
        for currentFile in glob.glob(os.path.join(path, '*')):
            if os.path.isdir(currentFile):
                self.remove_yaml_files(currentFile)
            if currentFile.endswith('.yaml'):
                os.remove(currentFile)

    def change_links(self, path='./specs'):
        """
        The converted .json files to .yaml files still have yaml pointer references
        to outer files and internal files , so as to resolve those again to json references
        this method is being used.
        :param path:
        :return:
        """
        for currentFile in glob.glob(os.path.join(path, '*')):
            if os.path.isdir(currentFile):
                self.change_links(currentFile)
            else:
                with open(currentFile) as f:
                    file_str = f.read()
                new_file_data = file_str.replace('.yaml', '.json')
                with open(currentFile, "w") as f:
                    f.write(new_file_data)

    def split(self):

        os.chdir(self.api_dir)
        run_js = open('split.js', 'w')
        run_js.write('var swag = require(\'swagger-split\');')
        run_js.write('swag.splitFile(\'api_spec.json\', 3, \'./specs\');')
        run_js.close()
        # -> the split.js file to be written  this file when executed gives the separated spec file in /specs folder
        os.system('node split.js')
        os.system(
            self.base_dir + '/node_modules/.bin/yaml2json -r specs --save --pretty')
        # the output of split.js will be in .yaml files hence this command is being used to
        # convert generated .yaml to .json files
        self.remove_yaml_files()
        self.change_links()
        os.remove('split.js')
