#!/usr/bin/env python


from distutils.core import setup
import os


###
### Basic settings for install
###

app_version = '0.5'
apps = ['hltlib', 'mailman', 'rolodex']
top_level_dir = os.getcwd()


###
### Install Arbre
###

setup(name='arbre',
      version=app_version,
      description='Python Library for managing communication/authorship datasets',
      author='James Dennis',
      author_email='jdennis@gmail.com',
      packages=['arbre', 'arbreapp'])


###
### Install Apps
###

for app in apps:
    os.chdir(top_level_dir + '/arbreapp/' + app)
    setup(name=app,
          version=app_version,
          author='James Dennis',
          author_email='jdennis@gmail.com',
          packages=['arbreapp.'+app],
          namespace_packages=['arbreapp'])

os.chdir(top_level_dir)
