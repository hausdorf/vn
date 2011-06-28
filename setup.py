#!/usr/bin/env python


from distutils.core import setup
import os
import fnmatch


###
### Settings
###

app_version = '0.5'

apps_dir = os.path.abspath('./arbreapp')


###
### Enumerate Packages
###

packages = ['arbre', 'arbreapp']

for app_name in os.listdir(apps_dir):
    app_path = os.path.join(apps_dir, app_name)
    if os.path.isdir(app_path):
        packages.append('arbreapp.' + app_name)


###
### Install Arbre
###

setup(name='arbre',
      version=app_version,
      description='Python Library for managing communication/authorship datasets',
      author='James Dennis',
      author_email='jdennis@gmail.com',
      packages=packages)
