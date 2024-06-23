# -*- coding: utf-8 -*-
"""
Unit tests for seedir.

Previously written for unittests, and updated for pytest.

Test methods MUST start with "test"
"""

import os

import seedir as sd

# realdir for testing on
testdir = os.path.dirname(os.path.abspath(__file__))

# ---- Test cases

print('\n--------------------'
      '\n\nTesting seedir.seedir() against {}\n\n'
      '--------------------'
      '\n'.format(testdir))

print('Basic seedir (depthlimit=2, itemlimit=10):\n')
sd.seedir(testdir, depthlimit=2, itemlimit=10)

print('\nDifferent Styles (depthlimit=1, itemlimit=5):')
for style in sd.STYLE_DICT.keys():
    print('\n{}:\n'.format(style))
    sd.seedir(testdir, style=style, depthlimit=1, itemlimit=5)

print('\nCustom Styles (depthlimit=1, itemlimit=5):')
sd.seedir(testdir, depthlimit=1, itemlimit=5, space='>>',
          split='>>', extend='II', final='->',
          folderstart='Folder: ', filestart='File: ')

print('\nDifferent Indents (depthlimit=1, itemlimit=5):')
for i in list(range(3)) + [8]:
    print('\nindent={}:\n'.format(str(i)))
    sd.seedir(testdir, depthlimit=1, itemlimit=5, indent=i)

print('\nItems Beyond Limit (depthlimit=1, itemlimit=1, beyond="content")')
sd.seedir(testdir, itemlimit=1, beyond='content')


