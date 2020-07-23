from django_swagger_utils.android_client_v2.constants import J2_APP_NAME_PREFIX
from django_swagger_utils.core.generators.generator import Generator

from django_swagger_utils.android_client_v2.generators_v2.android_generator_v2 import AndroidGeneratorV2


class AndroidJarDeploymentV2(Generator):
    def __init__(self, app_name, parser, paths, base_path):
        Generator.__init__(self, app_name, parser, paths, base_path)
        self.parser = parser
        self.paths = paths
        self.base_path = base_path
        self.app_name = app_name

    def jar_deployment_v2(self, vnum):
        """
                deploys a .jar file
                this .jar file is moved to a new folder android_jars in base_directory
                :return:
        """
        import os
        import shutil
        template_dir = os.getcwd() + "/maven_repo_%s" % self.app_name + J2_APP_NAME_PREFIX
        os.chdir(template_dir)
        os.system('mvn -U clean package')
        os.chdir(template_dir)
        android_gen = AndroidGeneratorV2(self.app_name, self.parser, self.paths, self.base_path)
        version = "0.0.%d" % vnum
        # deploys a jar file in target folder
        os.system("mvn deploy -s settings.xml")
        jar_path = template_dir + "/target/%s-%s.jar" % (self.app_name + J2_APP_NAME_PREFIX, version)
        os.chdir(os.environ["OLDPWD"])
        # creating new directory if not exists

        if not os.path.exists(self.paths["global_jars_dir"]):
            os.mkdir(self.paths["global_jars_dir"])
        # copying the jar file to android_jars directory
        shutil.copy2(jar_path, self.paths["global_jars_dir"])
        shutil.rmtree(template_dir)
