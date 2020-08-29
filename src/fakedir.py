# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:13:02 2020

@author: earne
"""
import os

import natsort
import random

from errors import FakedirError
import printing
from printing import words

def count_fakefiles(objs):
    files = sum([isinstance(p, FakeFile) for p in objs])
    return files

def count_fakedirs(objs):
    folders = sum([isinstance(p, FakeDir) for p in objs])
    return folders

def beyond_fakedepth_str(beyond, objs=None):
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

def recursive_fakedir_structure(fakedir, depth=0, incomplete=None, split='├─',
                                extend='│ ', space='  ', final='└─',
                                filestart='', folderstart='', depthlimit=None,
                                itemlimit=None, beyond=None, first=None,
                                sort=True, sort_reverse=False, sort_key=None,
                                include_folders=None, exclude_folders=None,
                                include_files=None, exclude_files=None,
                                regex=True):
    output = ''
    if incomplete is None:
        incomplete = []
    if depth == 0:
        output += folderstart + fakedir.name + os.sep +'\n'
    if depth == depthlimit and beyond is None:
        return output
    listdir = fakedir._children.copy()
    incomplete.append(depth)
    depth += 1
    if depthlimit and depth == depthlimit + 1:
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
        # listdir = sort_fakedir(listdir, first=first,
        #                        sort_reverse=sort_reverse, sort_key=sort_key)
    if any(isinstance(i, str) for i in [
            include_folders,
            exclude_folders,
            include_files,
            exclude_files]):
        keep = []
        for l in listdir:
            name = l.name
            if isinstance(l, FakeDir):
                if isinstance(include_folders, str):
                    if not printing.is_match(include_folders, name, regex):
                        continue
                if isinstance(exclude_folders, str):
                    if printing.is_match(exclude_folders, name, regex):
                        continue
            else:
                if isinstance(include_files, str):
                    if not printing.is_match(include_files, name, regex):
                        continue
                if isinstance(exclude_files, str):
                    if printing.is_match(exclude_files, name, regex):
                        continue
            keep.append(l)
        listdir = keep
    if not listdir:
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
    for i, f in enumerate(listdir):
        base_header = get_fakebase_header(incomplete, extend, space)
        if i == len(listdir) - 1:
            branch = final
            incomplete.remove(depth-1)
            incomplete = [n for n in incomplete if n < depth]
        elif itemlimit and i == itemlimit - 1 and beyond is None:
            branch = final
        else:
            branch = split
        header = base_header + branch
        if i == itemlimit:
            remaining = [rem for rem in listdir[i:]]
            if beyond is not None:
                extra = beyond_fakedepth_str(beyond, remaining)
                output += base_header + final + extra + '\n'
            return output
        if isinstance(f, FakeDir):
            output += header + folderstart + f.name + os.sep +'\n'
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
                                                 sort_reverse=sort_reverse,
                                                 sort_key=sort_key,
                                                 include_folders=include_folders,
                                                 exclude_folders=exclude_folders,
                                                 include_files=include_files,
                                                 exclude_files=exclude_files,
                                                 regex=regex)
        else:
            output += header + filestart + f.name + '\n'
    return output

class FakeItem:
    def __init__(self, name, parent=None):
        self.name = name
        self._parent = None
        self.parent = parent
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, other):
        if other:
            if not isinstance(other, FakeDir):
                raise FakedirError('other parameter must be instance of FakeDir')
            other._children.append(self)
        if self.parent is not None:
            self.parent._children.remove(self)
        self._parent = other

    def get_path(self):
        parents = [self.name]
        on = self
        while on.parent is not None:
            on = on.parent
            parents.append(on.name)
        return '/'.join(parents[::-1])

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
        super().__init__(name, parent)
        # alter children through FakeDir methods!
        self._children = []

    def __str__(self):
        return 'FakeFolder({})'.format(self.get_path())

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

    def show_children(self):
        print([i.name for i in self._children])

    def create_folder(self, name):
        FakeDir(name, parent=self)

    def create_file(self, name):
        FakeFile(name, parent=self)

    def seedir(self, style='lines', printout=False, indent=2, uniform='',
               depthlimit=None, itemlimit=None, beyond=None, first=None,
               sort=True, sort_reverse=False, sort_key=None,
               include_folders=None, exclude_folders=None, include_files=None,
               exclude_files=None, regex=True, **kwargs):
        if style:
            styleargs = printing.get_styleargs(style)
        styleargs = printing.format_indent(styleargs, indent=indent)
        if uniform:
            for arg in ['extend', 'split', 'final', 'space']:
                styleargs[arg] = uniform
        for k in kwargs:
            if k in styleargs:
                styleargs[k] = kwargs[k]
        if sort_key is not None or sort_reverse == True:
            sort = True
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
                                           **styleargs).strip()
        if printout:
            print(rfs)
        else:
            return rfs

def get_random_int(collection, seed=None):
    try:
        r = random.Random(seed).choice(collection)
        if not isinstance(r, int):
            raise TypeError('non int found')
        return r
    except Exception as e:
        raise(e)

def populate(fakedir, depth=3, folders=2, files=2, stopchance=.5, seed=None):
    random.seed(seed)
    if not isinstance(folders, int):
        try:
            fold_num = get_random_int(folders, seed=seed)
        except:
            raise FakedirError('folders must be an int or collection of int')
    if not isinstance(files, int):
        try:
            file_num = get_random_int(files, seed=seed)
        except:
            raise FakedirError('files must be an int or collection of int')
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

def randomfakedir(depth=2, files=range(1,4), folders=range(0,4), stopchance=.5, seed=None):
    top = FakeDir('MyFakeDir')
    populate(top, depth, folders, files, seed=seed, stopchance=stopchance)
    return top

x = randomfakedir()
x.seedir()

y = FakeDir('Salmon')