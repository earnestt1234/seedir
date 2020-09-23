#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup for seedir.

@author: Tom Earnest
"""

from setuptools import setup

setup(name='seedir',
      version='0.1',
      description='Package for creating, editing, and reading folder tree diagrams.',
      url='https://github.com/earnestt1234/seedir',
      author='Tom Earnest',
      author_email='earnestt1234@gmail.com',
      license='MIT',
      packages=['seedir'],
      install_requires=['emoji', 'natsort'],
      include_package_data=True,
      zip_safe=False,
      entry_points = {
        'console_scripts': ['seedir=seedir.command_line:main'],
        })

