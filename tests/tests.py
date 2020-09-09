# -*- coding: utf-8 -*-
"""
Unittests for seedir.

Run from PARENT directory on command line, i.e.:

seedir\  < here!
├─.git\
├─.gitignore
├─LICENSE
├─README.md
├─seedir\
├─seedirpackagetesting.py
├─stackoverflow.txt
└─tests\

With the command:
    python -m test.tests

Test methods MUST start with "test"
"""
import os
import unittest

import seedir as sd
from seedir.seedir import get_base_header

example = """mypkg/
    __init__.py
    app.py
    view.py
    test/
        __init__.py
        test_app.py
        test_view.py"""

example_with_comments="""mypkg/
    __init__.py #some comments
    app.py #####        more comments
    view.py #how about## this one
    test/
        __init__.py
        test_app.py
        test_view.py"""

try:
    testdir = os.path.join(os.environ['USERPROFILE'], 'Desktop')
except:
    try:
        testdir = os.environ['USERPROFILE']
    except:
        try:
            testdir = os.path.dirname(os.path.abspath(__file__))
        except:
            testdir = input('Cannot automatically find a directory for '
                            'testing seedir.seedir() - please enter a '
                            'path to test with depthlimit=1:\n')
            while not os.path.isdir(testdir):
                testdir = input('Not found, try again:\n')

class PrintSomeDirs(unittest.TestCase):
    print('\n--------------------'
          '\n\nTesting seedir.seedir() against {}:\n\n'
          '--------------------'
          '\n'.format(testdir))
    def test_a_print_userprofile(self):
        print('Basic seedir (depthlimit=2, itemlimit=10):\n')
        sd.seedir(testdir, depthlimit=2, itemlimit=10)

    def test_b_styles(self):
        print('\nDifferent Styles (depthlimit=1, itemlimit=5):')
        for style in sd.STYLE_DICT.keys():
            print('\n{}:\n'.format(style))
            sd.seedir(testdir, style=style, depthlimit=1, itemlimit=5)

    def test_c_custom_styles(self):
        print('\nCustom Styles (depthlimit=1, itemlimit=5):')
        sd.seedir(testdir, depthlimit=1, itemlimit=5, space='>>',
                  split='>>', extend='II', final='->',
                  folderstart='Folder: ', filestart='File: ')

    def test_d_indent(self):
        print('\nDifferent Indents (depthlimit=1, itemlimit=5):')
        for i in list(range(3)) + [8]:
            print('\nindent={}:\n'.format(str(i)))
            sd.seedir(testdir, depthlimit=1, itemlimit=5, indent=i)

    def test_e_beyond(self):
        print('\nItems Beyond Limit (depthlimit=1, itemlimit=1, beyond="content")')
        sd.seedir(testdir, itemlimit=1, beyond='content')

    def test_improper_kwargs(self):
        with self.assertRaises(sd.SeedirError):
            sd.seedir(testdir, spacing=False)

class TestSeedirStringFormatting(unittest.TestCase):
    def test_get_base_header(self):
        a = '| '
        b = '  '
        self.assertEqual('', get_base_header([0], a, b))
        self.assertEqual('| |   ', get_base_header([0, 1, 3], a, b))
        with self.assertRaises(ValueError):
            get_base_header([], a, b)

    def test_STYLE_DICT_members(self):
        keys = set(sd.STYLE_DICT.keys())
        self.assertEqual(keys, set(['lines', 'dash', 'spaces',
                                    'arrow', 'plus', 'emoji']))

    def test_get_style_args_all_accessible(self):
        styles = ['lines', 'dash', 'spaces',
                  'arrow', 'plus', 'emoji']
        for s in styles:
            d = sd.get_styleargs(s)
            self.assertTrue(isinstance(d, dict))
        with self.assertRaises(sd.SeedirError):
            d = sd.get_styleargs('missing_style')

    def test_get_style_args_deepcopy(self):
        x = sd.STYLE_DICT['lines']
        y = sd.get_styleargs('lines')
        self.assertTrue(x is not y)

    def test_format_indent(self):
        d = sd.get_styleargs('lines')
        f1 = sd.format_indent(d, indent=4)
        f2 = sd.format_indent(d, indent=1)
        chars = ['extend', 'space', 'split', 'final']
        self.assertTrue(all(len(f1[c])==4 for c in chars))
        self.assertTrue(all(len(f2[c])==1 for c in chars))

    def test_words_list(self):
        self.assertTrue(sd.words[0] == 'a')
        self.assertTrue(len(sd.words) == 25487)

class TestFakeDirReading(unittest.TestCase):
    def test_read_string(self):
        x = sd.fakedir_fromstring(example)
        self.assertTrue(isinstance(x, sd.FakeDir))

    def test_parse_comments(self):
        x = sd.fakedir_fromstring(example)
        y = sd.fakedir_fromstring(example_with_comments)
        z = sd.fakedir_fromstring(example_with_comments, parse_comments=False)
        self.assertEqual(x.get_child_names(), y.get_child_names())
        self.assertNotEqual(x.get_child_names(), z.get_child_names())

if __name__ == '__main__':
    unittest.main()