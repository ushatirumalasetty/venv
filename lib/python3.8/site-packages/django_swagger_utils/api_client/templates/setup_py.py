setup_template="""#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\\"]([^'\\"]*)['\\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

version = get_version('{{app_name}}_client', '__init__.py')

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()



required_list = []
extras_require = dict(library=['{{app_name}}'])

setup(
    name='{{app_name}}_client',
    version=version,
    description=\"\"\"Automated API generation from swagger\"\"\",
    long_description="",
    author='iB Hubs',
    author_email='devops@ibtspl.com',
    url='https://bitbucket.org/rahulsccl/{{app_name}}_backend-django',
    packages=[
        '{{app_name}}_client',
    ],
    include_package_data=True,
    install_requires=required_list,
    extras_require=extras_require,
    zip_safe=False,
    keywords='{{app_name}}',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

    ],
)
"""
