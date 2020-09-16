# -*- coding: utf-8 -*-
"""
Code for creating and editing "fake directories" within the seedir package;
i.e. coded representations of file trees.  The fakedir module can be used
to make example folder tree diagrams, read folder tree strings, or convert
abstract folder trees into real directories on a computer.  Many functions
and methods here repesent parallels to counterparts (for real directories)
in the seedir.seedir module.

@author: earne
"""
import os
import string
import re

import natsort
import random

from seedir.errors import FakedirError
import seedir.printing as printing
from seedir.printing import words
from seedir.seedir import sort_dir

def count_fakefiles(objs):
    '''
    Count the number of FakeFile objections in a collection.

    Parameters
    ----------
    objs : list-like
        Collection of objects (typically FakeDir and FakeFile).

    Returns
    -------
    files : int
        Count of FakeFile objects.

    '''
    files = sum([isinstance(p, FakeFile) for p in objs])
    return files

def count_fakedirs(objs):
    '''
    Count the number of FakeDir objections in a collection.

    Parameters
    ----------
    objs : list-like
        Collection of objects (typically FakeDir and FakeFile).

    Returns
    -------
    folders : int
        Count of FakeDir objects.

    '''
    folders = sum([isinstance(p, FakeDir) for p in objs])
    return folders

def beyond_fakedepth_str(beyond, objs=None):
    '''
    Generates the text for seedir.FakeDir.seedir() when using the 'beyond'
    parameter and ther are more items than the itemlimit or contents
    beyond the depthlimit.

    Parameters
    ----------
    beyond : str
        Style of beyond string to generate.  Options are:
            - 'ellipsis' ('...')
            - 'content' or 'contents' (the number of files and folders beyond)
            - a string starting with '_' (everything after the leading
              underscore will be returned)
    objs : collection of FakeDir and FakeFile objects, optional
        Objects beyond the limit, used when the 'beyond'
        argeument is 'content' or 'contents'. The default is None.

    Raises
    ------
    FakedirError
        Raised when the 'beyond' argument is not recognized.

    Returns
    -------
    str
        String indicating what lies beyond

    '''
    if beyond == 'ellipsis':
        return '...'
    elif beyond in ['contents','content']:
        folders = count_fakedirs(objs)
        files = count_fakefiles(objs)
        return '{} folder(s), {} file(s)'.format(folders, files)
    elif beyond and beyond[0] == '_':
        return beyond[1:]
    else:
        s1 = '"beyond" must be "ellipsis", "content", or '
        s2 = 'a string starting with "_"'
        raise FakedirError(s1 + s2)

def sort_fakedir(objs, first=None, sort_reverse=False, sort_key=None):
    '''
    Sorting function used by seedir.FakeDir.seedir() to sort contents when
    producing folder diagrams.

    Parameters
    ----------
    objs : list-like
        Collection of FakeDir or FakeFile objects to sort.
    first : 'files' or 'folders', optional
        Sort either (fake) files or folders first. The default is None.
    sort_reverse : bool, optional
        Reverse the sort applied. The default is False.
    sort_key : function, optional
        Function to apply to sort the objs by their name attribute (i.e. the
        folder or file name).  The function should take a string as a
        parameter.

    Raises
    ------
    SeedirError
        Fails when the 'first' parameter is used and no root directory
        is provided.

    Returns
    -------
    list
        Sorted input as a list.

    '''
    if sort_key is None:
            sort_key = lambda f : f.name
    else:
        y = sort_key
        sort_key = lambda f : y(f.name)
    if first in ['folders', 'files']:
        folders = [o for o in objs if isinstance(o, FakeDir)]
        files = [o for o in objs if isinstance(o, FakeFile)]
        folders = natsort.natsorted(folders, reverse=sort_reverse, key=sort_key)
        files = natsort.natsorted(files, reverse=sort_reverse, key=sort_key)
        return folders + files if first == 'folders' else files + folders
    else:
        return natsort.natsorted(objs, reverse=sort_reverse, key=sort_key)

def get_fakebase_header(incomplete, extend, space):
    base_header = []
    max_i = max(incomplete)
    for p in range(max_i):
        if p in incomplete:
            base_header.append(extend)
        else:
            base_header.append(space)
    return "".join(base_header)

def filter_item_names(listdir, include_folders=None,
                      exclude_folders=None, include_files=None,
                      exclude_files=None, regex=False):
    keep = []
    for l in listdir:
        if isinstance(l, FakeDir):
            if isinstance(include_folders, str):
                if not printing.is_match(include_folders, l.name, regex):
                    continue
            elif include_folders is not None:
                try:
                    if not any(printing.is_match(n, l.name, regex) for n in include_folders):
                        continue
                except:
                    raise FakedirError('Failure when trying to iterate '
                                       'over "include_folders" and '
                                       'match strings')
            if isinstance(exclude_folders, str):
                if printing.is_match(exclude_folders, l.name, regex):
                    continue
            elif exclude_folders is not None:
                try:
                    if any(printing.is_match(x, l.name, regex)
                           for x in exclude_folders):
                        continue
                except:
                    raise FakedirError('Failure when trying to iterate '
                                      'over "exclude_folders" and '
                                      'match strings')
        else:
            if isinstance(include_files, str):
                if not printing.is_match(include_files, l.name, regex):
                    continue
            elif include_files is not None:
                try:
                    if not any(printing.is_match(n, l.name, regex)
                               for n in include_files):
                        continue
                except:
                    raise FakedirError('Failure when trying to iterate '
                                      'over "include_files" and '
                                      'match strings')
            if isinstance(exclude_files, str):
                if printing.is_match(exclude_files, l.name, regex):
                    continue
            elif exclude_files is not None:
                try:
                    if any(printing.is_match(x, l.name, regex)
                           for x in exclude_files):
                        continue
                except:
                    raise FakedirError('Failure when trying to iterate '
                                      'over "exclude_files" and '
                                      'match strings')
        keep.append(l)
    return keep

def recursive_fakedir_structure(fakedir, depth=0, incomplete=None, split='├─',
                                extend='│ ', space='  ', final='└─',
                                filestart='', folderstart='', depthlimit=None,
                                itemlimit=None, beyond=None, first=None,
                                sort=True, sort_reverse=False, sort_key=None,
                                include_folders=None, exclude_folders=None,
                                include_files=None, exclude_files=None,
                                regex=False, slash='/'):
    output = ''
    if incomplete is None:
        incomplete = []
    if depth == 0:
        output += folderstart + fakedir.name + slash +'\n'
    if depth == depthlimit and beyond is None:
        return output
    listdir = fakedir._children.copy()
    incomplete.append(depth)
    depth += 1
    if depthlimit and depth > depthlimit:
        extra = beyond_fakedepth_str(beyond, listdir)
        if beyond is not None and extra:
            base_header = get_fakebase_header(incomplete, extend, space)
            output += base_header + final + extra + '\n'
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
        incomplete = [n for n in incomplete if n < depth]
        return output
    if sort or first is not None:
        pass
        listdir = sort_fakedir(listdir, first=first,
                               sort_reverse=sort_reverse, sort_key=sort_key)
    if any(arg is not None for arg in [
            include_folders,
            exclude_folders,
            include_files,
            exclude_files]):
        listdir = filter_item_names(listdir,
                                    include_folders=include_folders,
                                    exclude_folders=exclude_folders,
                                    include_files=include_files,
                                    exclude_files=exclude_files,
                                    regex=regex)
    if not listdir:
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
    for i, f in enumerate(listdir):
        if i == itemlimit:
            remaining = [rem for rem in listdir[i:]]
            if beyond is not None:
                extra = beyond_fakedepth_str(beyond, remaining)
                output += base_header + final + extra + '\n'
            return output
        base_header = get_fakebase_header(incomplete, extend, space)
        if i == len(listdir) - 1 or (itemlimit is not None and
                                     i == itemlimit - 1 and
                                     beyond is None):
            incomplete.remove(depth-1)
            incomplete = [n for n in incomplete if n < depth]
        if itemlimit and i == itemlimit - 1 and beyond is None:
            branch = final
        elif i == len(listdir) - 1:
            branch = final
        else:
            branch = split
        header = base_header + branch
        if isinstance(f, FakeDir):
            output += header + folderstart + f.name + slash +'\n'
            output += recursive_fakedir_structure(f, depth=depth,
                                                 incomplete=incomplete,
                                                 split=split, extend=extend,
                                                 space=space,
                                                 final=final,
                                                 filestart=filestart,
                                                 folderstart=folderstart,
                                                 depthlimit=depthlimit,
                                                 itemlimit=itemlimit,
                                                 beyond=beyond,
                                                 first=first,
                                                 sort=sort,
                                                 sort_reverse=sort_reverse,
                                                 sort_key=sort_key,
                                                 include_folders=include_folders,
                                                 exclude_folders=exclude_folders,
                                                 include_files=include_files,
                                                 exclude_files=exclude_files,
                                                 regex=regex,
                                                 slash=slash)
        else:
            output += header + filestart + f.name + '\n'
    return output

class FakeItem:
    def __init__(self, name, parent=None):
        self.name = name
        self._parent = None
        self.parent = parent
        self.depth = 0
        self.set_depth()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, other):
        if other:
            if not isinstance(other, FakeDir):
                raise FakedirError('other parameter must be instance of FakeDir')
            if self.name in other.get_child_names():
                raise FakedirError('FakeDirs must have unique file/folder names')
            other._children.append(self)
        if self.parent is not None:
            self.parent._children.remove(self)
        self._parent = other
        self.set_depth()
        if isinstance(self, FakeDir):
            self.set_child_depths()

    def get_path(self):
        parents = [self.name]
        on = self
        while on.parent is not None:
            on = on.parent
            parents.append(on.name)
        return '/'.join(parents[::-1])

    def set_depth(self):
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

class FakeFile(FakeItem):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.filename, self.extension = os.path.splitext(self.name)

    def __str__(self):
        return 'FakeFile({})'.format(self.get_path())

    def __repr__(self):
        return 'FakeFile({})'.format(self.get_path())

class FakeDir(FakeItem):
    def __init__(self, name, parent=None):
        # alter children through FakeDir methods!
        self._children = []
        super().__init__(name, parent)

    def __str__(self):
        return 'FakeDir({})'.format(self.get_path())

    def __repr__(self):
        return self.seedir(printout=False)

    def __getitem__(self, path):
        if type(path) not in [int, str]:
            raise FakedirError("Can only index FakeDir with int or str, "
                               "not {}".format(type(path)))
        paths = path.split('/')
        current = self
        for p in paths:
            for f in current._children:
                if p == f.name:
                    current = f
                    break
            else:
                raise(FakedirError('Path "{}" not found through {}'.format(path, self)))
        return current

    def create_folder(self, name):
        FakeDir(name, parent=self)

    def create_file(self, name):
        FakeFile(name, parent=self)

    def delete(self, child):
        target = None
        if type(child) in [FakeDir, FakeFile]:
            target = child.name
        elif isinstance(child, str):
            target = child
        if target is not None:
            try:
                to_del = next(f for f in self._children if f.name == target)
                to_del.parent = None
            except StopIteration:
                raise FakedirError('{} has no child with name "{}"'.format(self, target))
        else:
            child_copy = child.copy()
            for c in child_copy:
                target = None
                if type(c) in [FakeDir, FakeFile]:
                    target = c.name
                elif isinstance(c, str):
                    target = c
                if target is not None:
                    try:
                        to_del = next(f for f in self._children if f.name == target)
                        to_del.parent = None
                    except StopIteration:
                        raise FakedirError('{} has no child with name "{}"'.format(self, target))

    def get_child_names(self):
        return [c.name for c in self._children]

    def listdir(self):
        return self._children

    def realize(self, path=None):
        def create(f, root):
            fpath = f.get_path()
            joined = os.path.join(root, fpath)
            if isinstance(f, FakeDir):
                os.mkdir(joined)
            elif isinstance(f, FakeFile):
                with open(joined, 'w') as file:
                    pass
        if path is None:
            path = os.getcwd()
        os.mkdir(os.path.join(path, self.name))
        self.walk_apply(create, root=path)

    def seedir(self, style='lines', printout=True, indent=2, uniform=None,
               anystart=None, depthlimit=None, itemlimit=None, beyond=None,
               first=None, sort=False, sort_reverse=False, sort_key=None,
               include_folders=None, exclude_folders=None, include_files=None,
               exclude_files=None, regex=False, slash='/', **kwargs):
        accept_kwargs = ['extend', 'split', 'space', 'final',
                     'folderstart', 'filestart']
        if any(i not in accept_kwargs for i in kwargs.keys()):
            raise FakedirError('kwargs must be any of {}'.format(accept_kwargs))
        if style:
            styleargs = printing.get_styleargs(style)
        styleargs = printing.format_indent(styleargs, indent=indent)
        if uniform is not None:
            for arg in ['extend', 'split', 'final', 'space']:
                styleargs[arg] = uniform
        if anystart is not None:
            styleargs['folderstart'] = anystart
            styleargs['filestart'] = anystart
        for k in kwargs:
            if k in styleargs:
                styleargs[k] = kwargs[k]
        if sort_key is not None or sort_reverse == True:
            sort = True
        if slash.lower() in ['sep', 'os.sep']:
            slash = os.sep
        rfs =  recursive_fakedir_structure(self,
                                           depthlimit=depthlimit,
                                           itemlimit=itemlimit,
                                           beyond=beyond,
                                           first=first,
                                           sort=sort,
                                           sort_reverse=sort_reverse,
                                           sort_key=sort_key,
                                           include_folders=include_folders,
                                           exclude_folders=exclude_folders,
                                           include_files=include_files,
                                           exclude_files=exclude_files,
                                           regex=regex,
                                           slash=slash,
                                           **styleargs).strip()
        if printout:
            print(rfs)
        else:
            return rfs

    def set_child_depths(self):
            def apply_setdepth(FD):
                FD.set_depth()
            self.walk_apply(apply_setdepth)

    def trim(self, depthlimit):
        depthlimit = int(depthlimit)
        if depthlimit < 0:
            raise FakedirError('depthlimit must be non-negative int')
        depthlimit += self.depth
        def trim_apply(f, depthlimit):
            if depthlimit is not None and f.depth == depthlimit:
                if isinstance(f, FakeDir):
                    f.delete(f.listdir())
        if depthlimit == self.depth:
            self.delete(self.listdir())
        else:
            self.walk_apply(trim_apply, depthlimit=depthlimit)

    def walk_apply(self, foo, *args, **kwargs):
        for f in self._children:
            foo(f, *args, **kwargs)
            if isinstance(f, FakeDir):
                f.walk_apply(foo, *args, **kwargs)


def get_random_int(collection, seed=None):
    r = random.Random(seed).choice(collection)
    if not isinstance(r, int):
        raise TypeError('non int found')
    return r

def populate(fakedir, depth=3, folders=2, files=2, stopchance=.5, seed=None):
    random.seed(seed)
    if not isinstance(folders, int):
        try:
            fold_num = get_random_int(folders, seed=seed)
        except:
            raise FakedirError('folders must be an int or collection of int')
    else:
        fold_num = folders
    if not isinstance(files, int):
        try:
            file_num = get_random_int(files, seed=seed)
        except:
            raise FakedirError('files must be an int or collection of int')
    else:
        file_num = files
    for i in range(file_num):
        name = random.choice(words) + '.txt'
        while name in [f.name for f in fakedir._children]:
            name = random.choice(words) + '.txt'
        fakedir.create_file(name)
    for i in range(fold_num):
        name = random.choice(words)
        while name in [f.name for f in fakedir._children]:
            name = random.choice(words)
        fakedir.create_folder(name)
    for f in fakedir._children:
        if isinstance(f, FakeDir):
            if f.depth <= depth and random.uniform(0, 1) > stopchance:
                if seed:
                    seed += random.randint(1,100)
                populate(f, depth=depth, folders=folders, files=files, seed=seed,
                         stopchance=stopchance)

def randomdir(depth=2, files=range(1,4), folders=range(0,4), stopchance=.5, seed=None):
    top = FakeDir('MyFakeDir')
    populate(top, depth, folders, files, seed=seed, stopchance=stopchance)
    return top

def recursive_add_fakes(path, parent, depth=0, depthlimit=None,
                        itemlimit=None, first=None, sort=False,
                        sort_reverse=False, sort_key=None,
                        include_folders=None, exclude_folders=None,
                        include_files=None, exclude_files=None,
                        regex=False):
    if depthlimit is not None and depth >= depthlimit:
        return
    depth +=1
    listdir = os.listdir(path)
    if sort or first is not None:
        listdir = sort_dir(path, listdir, first=first,
                           sort_reverse=sort_reverse, sort_key=sort_key)
    if any(arg is not None for arg in [
            include_folders,
            exclude_folders,
            include_files,
            exclude_files]):
        listdir = printing.filter_item_names(path, listdir,
                                             include_folders=include_folders,
                                             exclude_folders=exclude_folders,
                                             include_files=include_files,
                                             exclude_files=exclude_files,
                                             regex=regex)
    for i, f in enumerate(listdir):
        if i == itemlimit:
            break
        sub = os.path.join(path, f)
        if os.path.isdir(sub):
            new = FakeDir(f, parent=parent)
            recursive_add_fakes(path=sub, parent=new, depth=depth,
                                depthlimit=depthlimit,
                                itemlimit=itemlimit,
                                include_folders=include_folders,
                                exclude_folders=exclude_folders,
                                include_files=include_files,
                                exclude_files=exclude_files, regex=regex)
        else:
            new = FakeFile(f, parent=parent)

def fakedir(path, depthlimit=None, itemlimit=None, first=None,
            sort=False, sort_reverse=False, sort_key=None,
            include_folders=None, exclude_folders=None, include_files=None,
            exclude_files=None, regex=True):
    if not os.path.isdir(path):
        raise FakedirError('path must be a directory')
    output = FakeDir(os.path.basename(path))
    recursive_add_fakes(path, parent=output, depthlimit=depthlimit,
                        itemlimit=itemlimit,
                        first=first,
                        sort=sort,
                        sort_reverse=sort_reverse,
                        sort_key=sort_key,
                        include_folders=include_folders,
                        exclude_folders=exclude_folders,
                        include_files=include_files,
                        exclude_files=exclude_files, regex=regex)
    return output

def fakedir_fromstring(s, start_chars=None, name_chars=None,
                       header_regex=None, name_regex=None,
                       supername='FakeDir', parse_comments=True):
    byline = s.split('\n')
    keyboard_chars = (string.ascii_letters + string.digits
                      + string.punctuation)
    filtered = "".join([c for c in keyboard_chars if c not in '/:?"*<>|'])
    if start_chars is None:
        start_chars = "".join([c for c in filtered if c not in '+=-'])
    if name_chars is None:
        name_chars = filtered + '\s' + '-'

    names = []
    headers = []
    depths = []

    for line in byline:
        if not line:
            continue
        if header_regex is None:
            header = re.match('.*?(?=[{}])'.format(start_chars), line).group()
        else:
            header = re.match(header_regex, line).group()
        depth = len(header)
        if name_regex is None:
            name = re.match('[{}]*'.format(name_chars), line[depth:]).group()
        else:
            name = re.match(name_regex, line).group()
        if '#' in name and parse_comments:
            name = re.match('.*?(?=#)', name).group().strip()
        if not name:
            continue

        headers.append(header)
        names.append(name)
        depths.append(depth)

    fakeitems = []
    superparent = None
    min_depth = min(depths)
    if len([d for d in depths if d == min_depth]) > 1:
        superparent = FakeDir(supername)
    min_depth_index1 = depths.index(min_depth)
    if any(i > min_depth for i in depths[:min_depth_index1]):
        superparent = FakeDir(supername)

    for i, name in enumerate(names):
        is_folder = False
        if name.strip()[-1] in ['/', '\\', os.sep]:
            is_folder = True
        if i < len(names) - 1:
            if depths[i + 1] > depths[i]:
                is_folder = True

        if depths[i] == min_depth:
            if is_folder:
                fakeitems.append(FakeDir(name, parent=superparent))
            else:
                fakeitems.append(FakeFile(name, parent=superparent))
        else:
            shallower = [d for d in depths[:i] if d < depths[i]]
            if shallower:
                max_shallower = max([d for d in depths[:i] if d < depths[i]])
                parent_index = max(idx for idx, val in enumerate(depths[:i])
                                   if val == max_shallower)
                parent = fakeitems[parent_index]
            else:
                parent = superparent
            if is_folder:
                fakeitems.append(FakeDir(name, parent=parent))
            else:
                fakeitems.append(FakeFile(name, parent=parent))

    if superparent is not None:
        return superparent
    else:
        idx = depths.index(min_depth)
        return fakeitems[idx]