
import os


class MergeSpec(object):
    '''
    class is being used to Merge the spec file
    '''

    def __init__(self, api_dir, base_dir):
        self.api_dir = api_dir
        self.base_dir = base_dir

    def merge(self):
        specs_dir = self.api_dir + "/specs/"
        from django_swagger_utils.core.utils.check_path_exists import check_path_exists
        if not check_path_exists(specs_dir):
            print("Split the spec file first :( [python manage.py build -S]")
            exit(1)
        os.chdir(specs_dir)  # ->go to the folder
        os.system(
            self.base_dir + '/node_modules/.bin/json2yaml index.json > index.yaml')  # ->only the root index.json needs to be in yaml hence converting it
        os.system(
            self.base_dir + '/node_modules/.bin/json-refs resolve -f index.yaml --filter relative > api_spec.json')  # resolve the json pointer refs in all files
        # only outer file refs will be resolved ,  not the inner file refs
        os.remove('index.yaml')
        # -> remove the index.yaml file after conversion is done
        os.chdir(self.api_dir)
        # move('/specs/api_spec.json','.')
