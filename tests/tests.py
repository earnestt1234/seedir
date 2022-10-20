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
    python -m tests.tests

Test methods MUST start with "test"
"""

import os
import unittest

import seedir as sd
from seedir.folderstructure import FakeDirStructure as FDS

# ---- Test seedir strings

example = """mypkg/
    __init__.py
    app.py
    view.py
    test/
        __init__.py
        test_app.py
        test_view.py"""

no_init = """mypkg/
    app.py
    view.py
    test/
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

# sd.randomdir(seed=456)
large_example = """MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/
│ ├─light.txt
│ ├─reliquary.txt
│ ├─sandal/
│ ├─paycheck/
│ │ ├─electrophoresis.txt
│ │ └─Pyongyang/
│ └─patrimonial/
├─Uganda/
└─pedantic/
  └─cataclysmic.txt"""

limit0_nobeyond = 'MyFakeDir/'

limit0_beyond_content = """MyFakeDir/
└─3 folder(s), 3 file(s)"""

depthlimit1 = '''MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/
├─Uganda/
└─pedantic/'''

depthlimit1_beyond_content = '''MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/
│ └─3 folder(s), 2 file(s)
├─Uganda/
│ └─0 folder(s), 0 file(s)
└─pedantic/
  └─0 folder(s), 1 file(s)'''

depthlimit1_beyond_content_exclude = '''MyFakeDir/
├─scrooge/
│ └─3 folder(s), 0 file(s)
├─Uganda/
│ └─0 folder(s), 0 file(s)
└─pedantic/
  └─0 folder(s), 0 file(s)'''

complex_sort = '''MyFakeDir/
├─monkish.txt
├─Vogel.txt
├─jowly.txt
├─pedantic/
│ └─cataclysmic.txt
├─scrooge/
│ ├─reliquary.txt
│ ├─light.txt
│ ├─patrimonial/
│ ├─paycheck/
│ │ ├─electrophoresis.txt
│ │ └─Pyongyang/
│ └─sandal/
└─Uganda/'''

complex_inclusion = '''MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/
│ ├─light.txt
│ └─sandal/
└─pedantic/'''

fmt_expand_single = '''MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/
│ ├─light.txt
│ ├─reliquary.txt
│ ├─sandal/
│ ├─paycheck/
│ │ ├─electrophoresis.txt
│ │ └─Pyongyang/
│ └─patrimonial/
├─Uganda/
└─pedantic/'''

fmt_expand_single_partial = '''MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/
│ ├─light.txt
│ ├─reliquary.txt
│ ├─sandal/
│ ├─paycheck/
│ └─patrimonial/
├─Uganda/
└─pedantic/'''

fmt_notbeyond = """MyFakeDir/
->Vogel.txt
└─3 folder(s), 2 file(s)"""

fmt_with_mask = '''MyFakeDir/
├─scrooge/
│ ├─light.txt
│ └─reliquary.txt
├─Uganda/
└─pedantic/
  └─cataclysmic.txt'''

# realdir for testing on
testdir = os.path.dirname(os.path.abspath(__file__))

# ---- Test cases

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
        with self.assertRaises(ValueError):
            sd.seedir(testdir, spacing=False)

class TestSeedirStringFormatting(unittest.TestCase):
    def test_get_base_header(self):
        a = '| '
        b = '  '
        self.assertEqual('', FDS.get_base_header([0], a, b))
        self.assertEqual('| |   ', FDS.get_base_header([0, 1, 3], a, b))
        with self.assertRaises(ValueError):
            FDS.get_base_header([], a, b)

    def test_STYLE_DICT_members(self):
        styles = ['lines', 'dash', 'spaces', 'arrow', 'plus']
        try:
            import emoji
            styles.append('emoji')
        except ImportError:
            pass
        keys = set(sd.STYLE_DICT.keys())
        self.assertEqual(keys, set(styles))

    def test_get_style_args_all_accessible(self):
        styles = ['lines', 'dash', 'spaces', 'arrow', 'plus']
        try:
            import emoji
            styles.append('emoji')
        except ImportError:
            pass
        for s in styles:
            d = sd.get_styleargs(s)
            self.assertTrue(isinstance(d, dict))
        with self.assertRaises(ValueError):
            d = sd.get_styleargs('missing_style')

    def test_get_style_args_deepcopy(self):
        x = sd.STYLE_DICT['lines']
        y = sd.get_styleargs('lines')
        self.assertTrue(x is not y)

    def test_format_indent(self):
        a = sd.get_styleargs('lines')
        b = sd.get_styleargs('lines')
        sd.printing.format_indent(a, indent=4)
        sd.printing.format_indent(b, indent=1)
        chars = ['extend', 'space', 'split', 'final']
        self.assertTrue(all(len(a[c])==4 for c in chars))
        self.assertTrue(all(len(b[c])==1 for c in chars))

    def test_words_list(self):
        self.assertTrue(sd.printing.words[0] == 'a')
        self.assertTrue(len(sd.printing.words) == 25487)

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

class TestFakeDir(unittest.TestCase):
    def test_count_fake_items(self):
        x = sd.fakedir_fromstring(example)
        self.assertEqual(FDS.count_folders(x.listdir()), 1)
        self.assertEqual(FDS.count_files(x.listdir()), 3)

    def test_sort_fakedir(self):
        x = sd.fakedir_fromstring(example).listdir()
        sort = FDS.sort_dir(x, sort_reverse=True, sort_key=lambda x : x[1])
        sort = [f.name for f in sort]
        correct = ['app.py', 'view.py', 'test', '__init__.py']
        self.assertEqual(sort, correct)

    def test_exclude_files_and_reread(self):
        x = sd.fakedir_fromstring(example)
        y = x.seedir(printout=False, exclude_files='.*\..*', regex=True)
        z = sd.fakedir_fromstring(y)
        self.assertEqual(set(z.get_child_names()), set(['test']))

    def test_include_files_and_reread(self):
        x = sd.fakedir_fromstring(example)
        y = x.seedir(printout=False, include_files=['app.py', 'view.py'],
                     regex=False)
        z = sd.fakedir_fromstring(y)
        self.assertEqual(set(z.get_child_names()),
                         set(['app.py', 'view.py', 'test', ]))

    def test_delete_string_names(self):
        x = sd.randomdir()
        x.delete(x.get_child_names())
        self.assertTrue(len(x.listdir()) == 0)

    def test_delete_objects(self):
        x = sd.randomdir()
        x.delete(x.listdir())
        self.assertTrue(len(x.listdir()) == 0)

    def test_set_parent(self):
        x = sd.fakedir_fromstring(example)
        x['test/test_app.py'].parent = x
        self.assertTrue('test_app.py' in x.get_child_names())

    def test_walk_apply(self):
        def add_0(f):
            f.name += ' 0'
        x = sd.fakedir_fromstring(example)
        x.walk_apply(add_0)
        for f in x.get_child_names():
            self.assertEqual(f[-1], '0')

    def test_depth_setting(self):
        x = sd.fakedir_fromstring(example)
        x['test'].create_folder('A')
        x['test/A'].create_folder('B')
        x['test/A/B'].create_file('boris.txt')
        self.assertEqual(x['test/A/B/boris.txt'].depth, 4)
        x['test/A/B/boris.txt'].parent = x
        self.assertEqual(x['boris.txt'].depth, 1)

    def test_randomdir_seed(self):
        x = sd.randomdir(seed=4.21)
        y = sd.randomdir(seed=4.21)
        self.assertEqual(x.get_child_names(), y.get_child_names())

    def test_populate_fakedir(self):
        x = sd.FakeDir('BORIS')
        self.assertFalse(x.get_child_names())
        sd.populate(x)
        self.assertTrue(x.get_child_names())

    def test_copy_equal(self):
        x = sd.randomdir(seed=7)
        y = x.copy()
        self.assertEqual(x.seedir(printout=False), y.seedir(printout=False))

    def test_copy_unlinked(self):
        def pallindrome(f):
            f.name = f.name + f.name[::-1]
        x = sd.fakedir_fromstring(large_example)

        before = x.seedir(printout=False)

        y = x.copy()
        y.walk_apply(pallindrome)

        after = x.seedir(printout=False)
        self.assertEqual(before, after)

class TestMask(unittest.TestCase):
    def test_mask_no_folders_or_files(self):
        def foo(x):
            if os.path.isdir(x) or os.path.isfile(x):
                return False

        s = sd.seedir(testdir, printout=False, depthlimit=2, itemlimit=10, mask=foo,)
        s = s.split('\n')
        self.assertEqual(len(s), 1)

    def test_mask_always_false(self):
        def bar(x):
            return False
        s = sd.seedir(testdir, printout=False, depthlimit=2, itemlimit=10, mask=bar)
        s = s.split('\n')
        self.assertEqual(len(s), 1)

    def test_mask_fakedir_fromstring(self):
        x = sd.fakedir_fromstring(example)
        s = x.seedir(printout=False, mask=lambda x : not x.name[0] == '_',
                     style='spaces', indent=4)
        self.assertEqual(no_init, s)

    def test_mask_fakedir(self):
        def foo(x):
            if os.path.isdir(x) or os.path.isfile(x):
                return False
        f = sd.fakedir(testdir, mask=foo)
        self.assertEqual(len(f.listdir()), 0)

class TestFolderStructure(unittest.TestCase):

    def test_many_randomdirs(self):
        seeds = range(1000)
        for i in seeds:
            r = sd.randomdir(seed=i)
            s = r.seedir(printout=False)
            f = sd.fakedir_fromstring(s)
            self.assertEqual(s, f.seedir(printout=False))

    def test_limit0_nobeyond(self):
        ans = limit0_nobeyond
        f = sd.fakedir_fromstring(large_example)
        s1 = f.seedir(printout=False, itemlimit=0)
        s2 = f.seedir(printout=False, depthlimit=0)
        self.assertEqual(ans, s1)
        self.assertEqual(ans, s2)

    def test_limit0_beyond_content(self):
        ans = limit0_beyond_content
        f = sd.fakedir_fromstring(large_example)
        s1 = f.seedir(printout=False, itemlimit=0, beyond='content')
        s2 = f.seedir(printout=False, depthlimit=0, beyond='content')
        self.assertEqual(ans, s1)
        self.assertEqual(ans, s2)

    def test_depthlimit1(self):
        ans = depthlimit1
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, depthlimit=1)
        self.assertEqual(ans, s)

    def test_depthlimit1_beyond_content(self):
        ans = depthlimit1_beyond_content
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, depthlimit=1, beyond='content')
        self.assertEqual(ans, s)

    def test_depthlimit1_beyond_content_exclude(self):
        ans = depthlimit1_beyond_content_exclude
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False,
                     depthlimit=1,
                     beyond='content',
                     exclude_files='.*\.txt',
                     regex=True)
        self.assertEqual(ans, s)

    def test_complex_sort(self):
        ans = complex_sort
        params = dict(sort=True, sort_reverse=True,
                      sort_key = lambda x: len(x), first='files')
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False,**params)
        self.assertEqual(ans, s)

    def test_complex_inclusion(self):
        ans = complex_inclusion
        params = dict(include_folders=['sandal', 'scrooge', 'pedantic'],
                      exclude_folders='sandal',
                      exclude_files='^Vogel',
                      include_files='^.[oi]',
                      regex=True)
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False,**params)
        self.assertEqual(ans, s)

class TestFormatter(unittest.TestCase):

    def test_formatter_beyond(self):

        def fmt(p):

            d = {'split':'->', 'final':'->'}

            return d

        ans = fmt_notbeyond
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, itemlimit=1, beyond='content', printout=False)
        self.assertEqual(s, ans)


    def test_formatter_no_return(self):

        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=lambda x: None, printout=False)
        self.assertEqual(s, large_example)

    def test_expand_one_folder_sticky(self):

        def fmt(p):

            d = {}
            if p.name == 'scrooge':
                d['depthlimit'] = None

            return d

        ans = fmt_expand_single
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, depthlimit=1, sticky_formatter=True, printout=False)
        self.assertEqual(ans, s)

    def test_expand_one_folder_nosticky(self):

        def fmt(p):

            d = {}
            if p.name == 'scrooge':
                d['depthlimit'] = None

            return d

        ans = fmt_expand_single_partial
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, depthlimit=1, printout=False)
        self.assertEqual(ans, s)

    def test_mask_with_fmt(self):

        def fmt(p):

            d = {}

            def case1(p):
                return not p.name.endswith('.txt')

            def case2(p):
                return p.name.endswith('.txt')

            if p.depth == 0:
                d['mask'] = case1

            else:
                d['mask'] = case2

            return d

        ans = fmt_with_mask
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, printout=False)
        self.assertEqual(s, ans)

if __name__ == '__main__':
    unittest.main()
