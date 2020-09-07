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
import unittest

import seedir as sd

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
    app.py #more comments
    view.py #     how about## this one
    test/
        __init__.py
        test_app.py
        test_view.py"""

class TestFakeDirFromString(unittest.TestCase):
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