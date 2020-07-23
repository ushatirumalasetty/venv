
import os
import shutil

from cookiecutter.main import cookiecutter
from io import open


class MobxNpmDeployment(object):
    '''
    MobxNpmDeployment class is used for the deployment purpose of generated Mobx Classes.
    only the app_name is taken which is necessary for the deployment.
    '''

    def __init__(self, app_name, paths, vnum):
        self.app_name = app_name
        self.paths = paths
        self.vnum = vnum
        self.folder_name = "mobx_classes_" + self.app_name

    def get_version(self):
        return "0.0.%d" % self.vnum

    def create_template(self):
        '''
        This method will create a cookiecutter template from the git repository . which will define a template for
        uploading of mobx-classes
        :return:
        '''

        clone_url = 'git@bitbucket.org:rahulsccl/swagger_mobx_generator.git'
        template_dir = cookiecutter(clone_url, extra_context={"app_name": self.app_name, "author": "iB-Hubs",
                                                              "version": self.get_version()},
                                    overwrite_if_exists=True, no_input=True)
        # shutil.copytree(self.paths["mobx_base_dir"], template_dir + '/lib/react/')
        # copy mobx_classes from build/mobx_classes to /lib/react in cookiecutter generated folder which is named app_name_mobxclasses
        shutil.copytree(self.paths["mobx_base_dir"], template_dir + '/lib/rn/')
        # copy the same classes in react and rn(react native) folder
        shutil.move(template_dir,
                    self.paths["build_dir"])  # moving cookiecutter generated folder from project_folder to app folder

    def compress_to_npm(self):
        '''
        generates the environment to for the uploading as npm package
        :return:
        '''
        os.chdir(os.path.join(self.paths["build_dir"], self.folder_name))
        # todo this babelrc is for web
        # babelrc_content = '''
        # {
        #  "presets": ["es2015", "react", "stage-0"],
        #  "plugins": ["transform-decorators-legacy"]
        # }
        # '''
        babelrc_content = '''
         { "presets": ["react-native", "flow"], "plugins": ["transform-decorators-legacy"], "retainLines": true }
        '''
        self.create_index_file_for_main()

        # babel is being used to babelify the generated files for react
        file1 = open(".babelrc", 'w')
        file1.write(babelrc_content)
        file1.close()
        os.system(
            "mv ~/.npmrc ~/.npmrc1")  # ->move the credentials of jfrog to other file so as to install below packages
        os.system("npm install babel-plugin-transform-decorators-legacy --save-dev")
        os.system("npm install babel-preset-react-native babel-preset-flow --save-dev")
        os.system("npm install babel-preset-env babel-preset-es2015 babel-preset-stage-0 babel-preset-react babel-cli")
        # os.system("npm run lib")
        # os.system("npm run del")
        # os.system("npm run move")
        os.system("mv ~/.npmrc1 ~/.npmrc")  # -> again move back for publishing
        os.system("npm publish")
        try:
            os.chdir(os.environ["OLDPWD"])
        except KeyError:
            pass

    def delete_previous(self):
        '''
        Method used to delete the folder of previous build.
        :return:
        '''
        try:
            if os.path.exists(os.path.join(self.paths["build_dir"], self.folder_name)):
                shutil.rmtree(os.path.join(self.paths["build_dir"], self.folder_name))
        except OSError as err:
            print(err)

    def get_immediate_subdirectories(self, directory):
        return [name for name in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, name))]

    def create_index_file_for_main(self):
        os.chdir(os.path.join(self.paths['build_dir'], self.folder_name, 'lib'))
        lib_directory = os.path.join(self.paths['build_dir'], self.folder_name, 'lib')
        content_for_index = []
        export_template = "export %s from '%s'"
        for each_sub_directory_in_lib in self.get_immediate_subdirectories(lib_directory):
            if each_sub_directory_in_lib == 'rn':  # only bablified files to be exported
                continue
            else:
                each_sub_directory_in_lib = 'rn'

            # todo Add import_string_1 = 'react' for react web
            import_string_1 = each_sub_directory_in_lib + '/'
            for each_type in self.get_immediate_subdirectories(os.path.join(lib_directory, each_sub_directory_in_lib)):
                import_string_2 = each_type
                for each_class in self.get_immediate_subdirectories(
                    os.path.join(lib_directory, each_sub_directory_in_lib, each_type)):
                    content_for_index.append(
                        export_template % (each_class, './' + import_string_1 + import_string_2 + '/' + each_class))
        index_file = open('index.js', 'w')
        for each_export_statement in content_for_index:
            index_file.write(each_export_statement + '\n')
        index_file.close()
        os.chdir(os.path.join(self.paths['build_dir'], self.folder_name))
