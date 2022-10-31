#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup for seedir.

@author: Tom Earnest
"""

from os import path

from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='seedir',
      version='0.4.0',
      description='Package for creating, editing, and reading folder tree diagrams.',
      url='https://github.com/earnestt1234/seedir',
      author='Tom Earnest',
      author_email='earnestt1234@gmail.com',
      license='MIT',
      packages=['seedir'],
      install_requires=['natsort'],
      extras_require={'emoji': ['emoji']},
      include_package_data=True,
      zip_safe=False,
      long_description=long_description,
      long_description_content_type='text/markdown',
      entry_points = {
        'console_scripts': ['seedir=seedir.command_line:main'],
        })
