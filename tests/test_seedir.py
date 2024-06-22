# -*- coding: utf-8 -*-
"""
Unit tests for seedir.

Previously written for unittests, and updated for pytest.

Test methods MUST start with "test"
"""

import os

import pytest

import seedir as sd
from seedir.errors import FakedirError
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

large_example_access_denied = """MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/ [ACCESS DENIED]
├─Uganda/ [ACCESS DENIED]
└─pedantic/ [ACCESS DENIED]"""

large_example_bummer = """MyFakeDir/
├─Vogel.txt
├─monkish.txt
├─jowly.txt
├─scrooge/<- BUMMER!
├─Uganda/<- BUMMER!
└─pedantic/<- BUMMER!"""

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

# variables
styles = ['lines', 'dash', 'spaces', 'arrow', 'plus', 'emoji']
try:
    import emoji
except ImportError:
    styles.remove('emoji')

# realdir for testing on
testdir = os.path.dirname(os.path.abspath(__file__))

# custom FakeDirStructure for testing errors
class ErrorRaisingFDS(FDS):

    def listdir(self, item):
        if self.isdir(item) and item.depth != 0:
            raise FakedirError('Oops!!!')
        else:
            return item.listdir()

# ---- Test cases

class PrintSomeDirs:

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
        with pytest.raises(ValueError):
            sd.seedir(testdir, spacing=False)

class TestSeedirStringFormatting:
    def test_get_base_header_0(self):
        a = '| '
        b = '  '
        assert FDS().get_base_header([0], a, b) == ''

    def test_get_base_header_013(self):
        a = '| '
        b = '  '
        assert FDS().get_base_header([0, 1, 3], a, b) == '| |   '

    def test_get_base_header_empty(self):
        a = '| '
        b = '  '
        assert FDS().get_base_header([], a, b) == ''

    def test_STYLE_DICT_members(self):
        keys = set(sd.STYLE_DICT.keys())
        assert keys == set(styles)

    @pytest.mark.parametrize('style', styles)
    def test_get_style_args_all_accessible(self, style):
        d = sd.get_styleargs(style)
        assert isinstance(d, dict)

    def test_access_missing_style(self):
        with pytest.raises(ValueError):
            _ = sd.get_styleargs('missing_style')

    def test_get_style_args_deepcopy(self):
        x = sd.STYLE_DICT['lines']
        y = sd.get_styleargs('lines')
        assert x is not y

    def test_format_indent_4(self):
        a = sd.get_styleargs('lines')
        sd.printing.format_indent(a, indent=4)
        chars = ['extend', 'space', 'split', 'final']
        assert all(len(a[c])==4 for c in chars)

    def test_format_indent_1(self):
        a = sd.get_styleargs('lines')
        sd.printing.format_indent(a, indent=1)
        chars = ['extend', 'space', 'split', 'final']
        assert all(len(a[c])==1 for c in chars)

    def test_words_list_start(self):
        assert sd.printing.words[0] == 'a'

    def test_words_list_length(self):
        assert len(sd.printing.words) == 25487

class TestFakeDirReading:
    def test_read_string(self):
        x = sd.fakedir_fromstring(example)
        assert isinstance(x, sd.FakeDir)

    def test_parse_comments_on(self):
        x = sd.fakedir_fromstring(example)
        y = sd.fakedir_fromstring(example_with_comments)
        assert x.get_child_names() == y.get_child_names()

    def test_parse_comments_off(self):
        x = sd.fakedir_fromstring(example)
        y = sd.fakedir_fromstring(example_with_comments, parse_comments=False)
        assert x.get_child_names() != y.get_child_names()

class TestFakeDir:
    def test_count_fake_folders(self):
        x = sd.fakedir_fromstring(example)
        assert FDS().count_folders(x.listdir()) == 1

    def test_count_fake_files(self):
        x = sd.fakedir_fromstring(example)
        assert FDS().count_files(x.listdir()) == 3

    def test_sort_fakedir(self):
        x = sd.fakedir_fromstring(example).listdir()
        sort = FDS().sort_dir(x, sort_reverse=True, sort_key=lambda x : x[1])
        sort = [f.name for f in sort]
        correct = ['app.py', 'view.py', 'test', '__init__.py']
        assert sort == correct

    def test_exclude_files_and_reread(self):
        x = sd.fakedir_fromstring(example)
        y = x.seedir(printout=False, exclude_files=r'.*\..*', regex=True)
        z = sd.fakedir_fromstring(y)
        assert set(z.get_child_names()) == set(['test'])

    def test_include_files_and_reread(self):
        x = sd.fakedir_fromstring(example)
        y = x.seedir(printout=False, include_files=['app.py', 'view.py'],
                      regex=False)
        z = sd.fakedir_fromstring(y)
        assert set(z.get_child_names()) == set(['app.py', 'view.py', 'test', ])

    def test_delete_string_names(self):
        x = sd.randomdir()
        x.delete(x.get_child_names())
        assert len(x.listdir()) == 0

    def test_delete_objects(self):
        x = sd.randomdir()
        x.delete(x.listdir())
        assert len(x.listdir()) == 0

    def test_set_parent(self):
        x = sd.fakedir_fromstring(example)
        x['test/test_app.py'].parent = x
        assert 'test_app.py' in x.get_child_names()

    def test_walk_apply(self):
        def add_0(f):
            f.name += ' 0'
        x = sd.fakedir_fromstring(example)
        x.walk_apply(add_0)
        last_chars = [f[-1] for f in x.get_child_names()]
        assert set(last_chars) == set('0')

    def test_depth_setting(self):
        x = sd.fakedir_fromstring(example)
        x['test'].create_folder('A')
        x['test/A'].create_folder('B')
        x['test/A/B'].create_file('boris.txt')
        obj = x['test/A/B/boris.txt']
        depth_a = obj.depth
        obj.parent = x
        depth_b = obj.depth
        assert (depth_a, depth_b) == (4, 1)

    def test_randomdir_seed(self):
        x = sd.randomdir(seed=4.21)
        y = sd.randomdir(seed=4.21)
        assert x.get_child_names() == y.get_child_names()

    def test_empty_fakedir_has_no_children(self):
        x = sd.FakeDir('BORIS')
        assert len(x.get_child_names()) == 0

    def test_populate_adds_children(self):
        x = sd.FakeDir('BORIS')
        sd.populate(x)
        assert len(x.get_child_names()) > 0

    def test_copy_equal(self):
        x = sd.randomdir(seed=7)
        y = x.copy()
        assert x.seedir(printout=False) == y.seedir(printout=False)

    def test_copy_unlinked(self):
        def pallindrome(f):
            f.name = f.name + f.name[::-1]
        x = sd.fakedir_fromstring(large_example)

        before = x.seedir(printout=False)

        y = x.copy()
        y.walk_apply(pallindrome)

        after = x.seedir(printout=False)
        assert before == after

class TestMask:
    def test_mask_no_folders_or_files(self):
        def foo(x):
            if os.path.isdir(x) or os.path.isfile(x):
                return False

        s = sd.seedir(testdir, printout=False, depthlimit=2, itemlimit=10, mask=foo,)
        s = s.split('\n')
        assert len(s) == 1

    def test_mask_always_false(self):
        def bar(x):
            return False
        s = sd.seedir(testdir, printout=False, depthlimit=2, itemlimit=10, mask=bar)
        s = s.split('\n')
        assert len(s) == 1

    def test_mask_fakedir_fromstring(self):
        x = sd.fakedir_fromstring(example)
        s = x.seedir(printout=False, mask=lambda x : not x.name[0] == '_',
                     style='spaces', indent=4)
        assert no_init == s

    def test_mask_fakedir(self):
        def foo(x):
            if os.path.isdir(x) or os.path.isfile(x):
                return False
        f = sd.fakedir(testdir, mask=foo)
        assert len(f.listdir()) == 0

class TestFolderStructure:

    def test_many_randomdirs(self):
        seeds = range(1000)
        results = []
        for i in seeds:
            r = sd.randomdir(seed=i)
            s = r.seedir(printout=False)
            f = sd.fakedir_fromstring(s)
            results.append(s == f.seedir(printout=False))
        assert all(results)

    def test_itemlimit0_nobeyond(self):
        ans = limit0_nobeyond
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, itemlimit=0)
        assert ans == s

    def test_depthlimit0_nobeyond(self):
        ans = limit0_nobeyond
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, depthlimit=0)
        assert ans == s

    def test_itemlimit0_beyond_content(self):
        ans = limit0_beyond_content
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, itemlimit=0, beyond='content')
        assert ans == s

    def test_depthlimit0_beyond_content(self):
        ans = limit0_beyond_content
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, depthlimit=0, beyond='content')
        assert ans == s

    def test_depthlimit1(self):
        ans = depthlimit1
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, depthlimit=1)
        assert ans == s

    def test_depthlimit1_beyond_content(self):
        ans = depthlimit1_beyond_content
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False, depthlimit=1, beyond='content')
        assert ans == s

    def test_depthlimit1_beyond_content_exclude(self):
        ans = depthlimit1_beyond_content_exclude
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False,
                      depthlimit=1,
                      beyond='content',
                      exclude_files=r'.*\.txt',
                      regex=True)
        assert ans == s

    def test_complex_sort(self):
        ans = complex_sort
        params = dict(sort=True, sort_reverse=True,
                      sort_key = lambda x: len(x), first='files')
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False,**params)
        assert ans == s

    def test_complex_inclusion(self):
        ans = complex_inclusion
        params = dict(include_folders=['sandal', 'scrooge', 'pedantic'],
                      exclude_folders='sandal',
                      exclude_files='^Vogel',
                      include_files='^.[oi]',
                      regex=True)
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(printout=False,**params)
        assert ans == s

class TestFormatter:

    def test_formatter_beyond(self):

        def fmt(p):

            d = {'split':'->', 'final':'->'}

            return d

        ans = fmt_notbeyond
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, itemlimit=1, beyond='content', printout=False)
        assert s == ans


    def test_formatter_no_return(self):

        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=lambda x: None, printout=False)
        assert s == large_example

    def test_expand_one_folder_sticky(self):

        def fmt(p):

            d = {}
            if p.name == 'scrooge':
                d['depthlimit'] = None

            return d

        ans = fmt_expand_single
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, depthlimit=1, sticky_formatter=True, printout=False)
        assert ans == s

    def test_expand_one_folder_nosticky(self):

        def fmt(p):

            d = {}
            if p.name == 'scrooge':
                d['depthlimit'] = None

            return d

        ans = fmt_expand_single_partial
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(formatter=fmt, depthlimit=1, printout=False)
        assert ans == s

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
        assert s == ans

class TestTupleItemLimit:

    def count_folder_children(self, f):
        output = []
        foo = lambda x: output.append(len([a for a in f.listdir() if a.isdir()]))
        f.walk_apply(foo)
        return output

    def count_file_children(self, f):
        output = []
        foo = lambda x: output.append(len([a for a in f.listdir() if not a.isdir()]))
        f.walk_apply(foo)
        return output

    def make_letter_example(self):
        f = sd.FakeDir('example')
        f.create_folder(['a', 'b', 'c', 'd'])
        f.create_file(['e', 'f', 'g', 'h'])
        return f

    def test_None_None(self):
        f = sd.fakedir_fromstring(large_example)
        normal = f.seedir(printout=False)
        test = f.seedir(itemlimit=(None, None), printout=False)
        assert normal == test

    def test_None_1(self):
        start = sd.fakedir_fromstring(large_example)
        s = start.seedir(itemlimit=(None, 1), first='files', printout=False)
        end = sd.fakedir_fromstring(s)
        ans = self.count_file_children(end)
        assert all([x <= 1 for x in ans])

    def test_1_None(self):
        start = sd.fakedir_fromstring(large_example)
        s = start.seedir(itemlimit=(1, None), first='folders', printout=False)
        end = sd.fakedir_fromstring(s)
        ans = self.count_folder_children(end)
        assert all([x <= 1 for x in ans])

    def test_1_1(self):
        start = sd.fakedir_fromstring(large_example)
        s = start.seedir(itemlimit=(1, None), first='folders', printout=False)
        end = sd.fakedir_fromstring(s)
        ans = self.count_folder_children(end)
        assert all([x <= 1 for x in ans])

    def test_filter_letter_example_2_2(self):
        e = self.make_letter_example()
        s = e.seedir(itemlimit=(2, 2), sort=True, printout=False)
        f = sd.fakedir_fromstring(s)
        assert set(f.get_child_names()) == set(['a', 'b', 'e', 'f'])

    def test_filter_letter_example_2_None(self):
        e = self.make_letter_example()
        s = e.seedir(itemlimit=(2, None), sort=True, printout=False)
        f = sd.fakedir_fromstring(s)
        assert set(f.get_child_names()) == set(['a', 'b', 'e', 'f', 'g', 'h'])

    def test_filter_letter_example_None_0(self):
        e = self.make_letter_example()
        s = e.seedir(itemlimit=(None, 0), sort=True, printout=False)
        f = sd.fakedir_fromstring(s)
        assert set(f.get_child_names()) == set(['a', 'b', 'c', 'd'])

    def test_filter_letter_example_0_0(self):
        e = self.make_letter_example()
        s = e.seedir(itemlimit=(0, 0), sort=True, printout=False)
        f = sd.fakedir_fromstring(s)
        assert len(f.get_child_names()) == 0

    def test_works_with_list(self):
        f = sd.fakedir_fromstring(large_example)
        s = f.seedir(itemlimit=[0, None], printout=False)
        split = s.split('\n')
        endswithtxt = [x.endswith('txt') for x in split[1:]]
        assert all(endswithtxt)

class TestErrorHandlingArgs:

    def test_handle_errors_correct_type(self):
        x = ErrorRaisingFDS()
        f = sd.fakedir_fromstring(large_example)
        s = x(f, printout=False,
              acceptable_listdir_errors=FakedirError,
              denied_string=' [ACCESS DENIED]')
        assert s == large_example_access_denied

    def test_handle_errors_incorrect_type(self):
        x = ErrorRaisingFDS()
        f = sd.fakedir_fromstring(large_example)
        with pytest.raises(sd.errors.FakedirError):
            _ = x(f, printout=False,
                  acceptable_listdir_errors=PermissionError,
                  denied_string=' [ACCESS DENIED]')

    def test_handle_errors_None(self):
        x = ErrorRaisingFDS()
        f = sd.fakedir_fromstring(large_example)
        with pytest.raises(sd.errors.FakedirError):
            _ = x(f, printout=False,
                  acceptable_listdir_errors=None,
                  denied_string=' [ACCESS DENIED]')

    def test_handle_errors_tuple(self):
        x = ErrorRaisingFDS()
        f = sd.fakedir_fromstring(large_example)
        s = x(f, printout=False,
              acceptable_listdir_errors=(FakedirError, PermissionError),
              denied_string=' [ACCESS DENIED]')
        assert s == large_example_access_denied

    def test_handle_errors_different_string(self):
        x = ErrorRaisingFDS()
        f = sd.fakedir_fromstring(large_example)
        s = x(f, printout=False,
              acceptable_listdir_errors=FakedirError,
              denied_string='<- BUMMER!')
        assert s == large_example_bummer

