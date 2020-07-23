import os
import shutil


def copy_directory(src, dest):
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print(('Directory not copied. Error: %s' % e))
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print(('Directory not copied. Error: %s' % e))


def rm_directory(src):
    if os.path.exists(src):
        shutil.rmtree(src)
