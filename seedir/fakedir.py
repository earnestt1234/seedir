# -*- coding: utf-8 -*-
"""
Code for creating and editing "fake directories" within the `seedir` package;
i.e. Python folder tree objects.  This module can be used
to make example folder tree diagrams, read folder tree strings, or convert
abstract folder trees into real directories on a computer.
"""

__pdoc__ = {'get_random_int': False,
            'recursive_add_fakes': False}

import os
import string
import re

import random

from seedir.errors import FakedirError
from seedir.folderstructure import FakeDirStructure, RealDirStructure
from seedir.folderstructure import listdir_fullpath

from seedir.printing import words

class FakeItem:
    '''Parent class for representing fake folders and files.'''
    def __init__(self, name, parent=None):
        '''
        Initialize the fake diretory or file object.

        Parameters
        ----------
        name : str
            Name for the folder or file.
        parent : seedir.fakedir.FakeDir or None, optional
            Parent of `self`. The default is `None`, meaning the object will
            be the "root" of the directory.

        Returns
        -------
        None.

        '''
        self.name = name
        self._parent = None
        self.parent = parent
        self.depth = 0
        self.set_depth()

    @property
    def parent(self):
        '''
        Getter for the `parent` attribute.

        Returns
        -------
        seedir.fakedir.FakeDir
            The parent folder of the object.

        '''
        return self._parent

    @parent.setter
    def parent(self, other):
        '''
        Setter for the `parent` attribute.

        When a new parent is assigned for an object, this method
        verifies that the other object is `seedir.fakedir.FakeDir`, and that the other
        objects children do not contain a fake item with the same name.

        If those conditions are met, `self` is removed from the children
        of its current parent, and its parent attribute is reassigned.
        Depths are also reset.

        Parameters
        ----------
        other : seedir.fakedir.FakeDir
            Fake directory to become the new `parent` for self.

        Raises
        ------
        TypeError
            other is not a `seedir.fakedir.Fakedir`.

        FakedirError
            Name collision: `self.name` is in the child names of other.


        Returns
        -------
        None.

        '''
        if other:
            if not isinstance(other, FakeDir):
                raise TypeError('other parameter must be instance of FakeDir')
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
        '''Return a "path" string of self, from the head `seedir.fakedir.FakeDir`
        (which has `parent == None`).

        ```
        >>> import seedir as sd
        >>> f = sd.randomdir(seed=5) # create a random FakeDir
        >>> f
        MyFakeDir/
        ├─senor.txt
        ├─verb.txt
        ├─takeoff.txt
        ├─monastic/
        │ ├─paddy.txt
        │ ├─ewe.txt
        │ ├─advantage.txt
        │ ├─hooves/
        │ └─registrar/
        └─zag/
          ├─thematic.txt
          ├─inelastic.txt
          ├─fierce.txt
          ├─gout/
          └─stein/
            ├─vector.txt
            ├─sora.txt
            └─proviso.txt

        >>> x = sd.FakeDir('newfolder', parent=f['zag/stein'])
        >>> x.get_path()
        'MyFakeDir/zag/stein/newfolder'

        ```

        '''
        parents = [self.name]
        on = self
        while on.parent is not None:
            on = on.parent
            parents.append(on.name)
        return '/'.join(parents[::-1])

    def set_depth(self):
        '''Set the depth attribute of `self`, based on the depth of parent.
        Automatically called when setting new parents.'''
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

    def isfile(self):
        """Returns `True` if instance is a `seedir.fakedir.FakeFile` object"""
        return isinstance(self, FakeFile)

    def isdir(self):
        """Returns True if instance is a `seedir.fakedir.FakeDir` object"""
        return isinstance(self, FakeDir)

    def siblings(self):
        """Returns all the other children of `self.parent`."""
        if self.parent is None:
            return []
        else:
            return [f for f in self.parent.listdir() if f is not self]

class FakeFile(FakeItem):
    '''Class to represent files in `seedir.fakedir.FakeDir` objects.

    Files in a `seedir.fakedir.FakeDir` have this type.

    ```
    >>> import seedir as sd
    >>> f = sd.randomdir(seed=5) # create a random FakeDir
    >>> f
    MyFakeDir/
    ├─senor.txt
    ├─verb.txt
    ├─takeoff.txt
    ├─monastic/
    │ ├─paddy.txt
    │ ├─ewe.txt
    │ ├─advantage.txt
    │ ├─hooves/
    │ └─registrar/
    └─zag/
      ├─thematic.txt
      ├─inelastic.txt
      ├─fierce.txt
      ├─gout/
      └─stein/
        ├─vector.txt
        ├─sora.txt
        └─proviso.txt

    >>> f['senor.txt']
    FakeFile(MyFakeDir/senor.txt)

    ```

    '''
    def __init__(self, name, parent=None):
        '''Same as `seedir.fakedir.FakeItem` initialization, but adds
        `filename` and `extension` attributes.
        '''
        super().__init__(name, parent)
        self.filename, self.extension = os.path.splitext(self.name)

    def __str__(self):
        return 'FakeFile({})'.format(self.get_path())

    def __repr__(self):
        return 'FakeFile({})'.format(self.get_path())

class FakeDir(FakeItem):
    '''Class to represent fake folders.  Can be used to create
    custom folder tree diagrams.  See `seedir.fakedir.fakedir()` for converting
    a real directory into a FakeDir, `seedir.fakedir.fakedir_fromstring()` for
    converting a text folder diagram into a `FakeDir`, and `seedir.fakedir.randomdir()`
    for creating a random one.

    To make a `FakeDir` from scratch, use this class:

    ```
    >>> import seedir as sd
    >>> x = sd.FakeDir('myfakedir')
    >>> x.seedir()
    myfakedir/

    ```

    There are various ways to add to it:

    ```
    # using methods; the created items are returned
    >>> x.create_file(['__init__.py', 'main.py', 'styles.txt'])
    [FakeFile(myfakedir/__init__.py), FakeFile(myfakedir/main.py), FakeFile(myfakedir/styles.txt)]
    >>> x.create_folder('docs')
    docs/

    # initializing new objects and setting the parent
    >>> y = sd.FakeDir('resources', parent=x)

    # changing the parent of existing objects
    >>> z = sd.FakeDir('images')
    >>> z.parent = y

    >>> for n in ['a', 'b', 'c']:
    ...     z.create_file(n + '.png')
    FakeFile(myfakedir/resources/images/a.png)
    FakeFile(myfakedir/resources/images/b.png)
    FakeFile(myfakedir/resources/images/c.png)

    >>> x.seedir(sort=True, first='folders')
    myfakedir/
    ├─docs/
    ├─resources/
    │ └─images/
    │   ├─a.png
    │   ├─b.png
    │   └─c.png
    ├─__init__.py
    ├─main.py
    └─styles.txt

    ```

    You can index with path-like strings:

    ```
    >>> x['resources/images/a.png']
    FakeFile(myfakedir/resources/images/a.png)

    ```

    '''
    def __init__(self, name, parent=None):
        '''Same as `seedir.fakedir.FakeItem` initialization, but adds
        the `_children` attribute for keeping track of items inside the fake dir.
        '''
        # alter children through FakeDir methods!
        self._children = []
        super().__init__(name, parent)

    def __str__(self):
        '''String conversion of `FakeDir`'''
        return 'FakeDir({})'.format(self.get_path())

    def __repr__(self):
        '''Representation of `FakeDir` (shown as a folder diagram).'''
        return self.seedir(printout=False)

    def __getitem__(self, path):
        """Use path-like strings to index `FakeDir` objects."""
        if not isinstance(path, str):
            raise TypeError("Can only index FakeDir with int or str, "
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
        """
        Create a new folder (`seedir.fakedir.FakeDir`) as a child.

        ```
        >>> import seedir as sd
        >>> x = sd.FakeDir('Test')
        >>> x.create_folder("new_folder")
        new_folder/
        >>> x.seedir()
        Test/
        └─new_folder/

        ```

        Parameters
        ----------
        name : str
            Name of the new folder.  Can also be a collection of names to create
            multiple folders.

        Returns
        -------
        FakeDir or list
            The new object or objects (as a list) are returned.

        """
        if isinstance(name, str):
            return FakeDir(name, parent=self)
        else:
            return [FakeDir(s, parent=self) for s in name]

    def create_file(self, name):
        """
        Create a new file (`seedir.fakedir.FakeFile`) as a child.

        ```
        >>> import seedir as sd
        >>> x = sd.FakeDir('Test')
        >>> x.create_file("new_file.txt")
        FakeFile(Test/new_file.txt)
        >>> x.seedir()
        Test/
        └─new_file.txt

        ```

        Parameters
        ----------
        name : str
            Name of the new file.  Can also be a collection of names to create
            multiple files.

        Returns
        -------
        FakeFile or list
            The new object or objects (as a list) are returned.

        """
        if isinstance(name, str):
            return FakeFile(name, parent=self)
        else:
            return [FakeFile(s, parent=self) for s in name]

    def copy(self):
        '''
        Generate a totally unlinked copy object.  The root of the new FakeDir
        will be a copy of this folder (and all its subfolders).  Calling this
        method does not alter self at all.

        Returns
        -------
        seedir.fakedir.FakeDir
            A copy FakeDir.

        '''
        def recurse_build(f, other):
            '''Recursive helper for building the new copy.'''
            if f.isfile():
                new = FakeFile(name=f.name, parent=other)
            elif f.isdir():
                new = FakeDir(name=f.name, parent=other)
                for child in f.listdir():
                    recurse_build(child, other=new)
            return new

        return recurse_build(self, other=None)


    def delete(self, child):
        '''
        Delete items from a `seedir.fakedir.FakeDir`.

        ```
        >>> import seedir as sd
        >>> r = sd.randomdir(seed=5)
        >>> r
        MyFakeDir/
        ├─senor.txt
        ├─verb.txt
        ├─takeoff.txt
        ├─monastic/
        │ ├─paddy.txt
        │ ├─ewe.txt
        │ ├─advantage.txt
        │ ├─hooves/
        │ └─registrar/
        └─zag/
          ├─thematic.txt
          ├─inelastic.txt
          ├─fierce.txt
          ├─gout/
          └─stein/
            ├─vector.txt
            ├─sora.txt
            └─proviso.txt

        >>> r['zag'].delete(['thematic.txt', 'inelastic.txt']) # delete with string names
        >>> r.delete(r['monastic']) # delete with objects
        >>> r
        MyFakeDir/
        ├─senor.txt
        ├─verb.txt
        ├─takeoff.txt
        └─zag/
          ├─fierce.txt
          ├─gout/
          └─stein/
            ├─vector.txt
            ├─sora.txt
            └─proviso.txt

        ```

        Parameters
        ----------
        child : str, FakeDir, FakeFile or list-like
            Child or children to remove.  Can be a string name, actual
            `seedir.fakedir.FakeDir` / `seedir.fakedir.FakeFile` object,
            or a collection of names or items.

        Raises
        ------
        FakedirError
            No item found to delete.

        Returns
        -------
        None.

        '''
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
            child_copy = [c for c in child]
            for c in child_copy:
                target = None
                if type(c) in [FakeDir, FakeFile]:
                    target = c.name
                elif isinstance(c, str):
                    target = c
                if target is not None:
                    try:
                        to_del = next(f for f in self._children if
                                      f.name == target)
                        to_del.parent = None
                    except StopIteration:
                        raise FakedirError('{} has no child with name "{}"'.format(self, target))

    def get_child_names(self):
        '''Return a list of child names.

        ```
        >>> import seedir as sd
        >>> r = sd.randomdir(seed=5)
        >>> r
        MyFakeDir/
        ├─senor.txt
        ├─verb.txt
        ├─takeoff.txt
        ├─monastic/
        │ ├─paddy.txt
        │ ├─ewe.txt
        │ ├─advantage.txt
        │ ├─hooves/
        │ └─registrar/
        └─zag/
          ├─thematic.txt
          ├─inelastic.txt
          ├─fierce.txt
          ├─gout/
          └─stein/
            ├─vector.txt
            ├─sora.txt
            └─proviso.txt

        >>> r.get_child_names()
        ['senor.txt', 'verb.txt', 'takeoff.txt', 'monastic', 'zag']

        ```

        '''
        return [c.name for c in self._children]

    def listdir(self):
        '''Return the list of `seedir.fakedir.FakeFile` and `seedir.fakedir.FakeDir`
        objects that are children of `self` (like `os.listdir`).

        ```
        >>> import seedir as sd
        >>> r = sd.randomdir(seed=1)
        >>> r
        MyFakeDir/
        ├─churchmen.txt
        └─exposure/

        >>> print([str(i) for i in r.listdir()])
        ['FakeFile(MyFakeDir/churchmen.txt)', 'FakeDir(MyFakeDir/exposure)']

        ```
        '''
        return self._children

    def realize(self, path=None):
        '''
        Convert a fake file tree into a real one by creating a folder at a
        given path, and populating it with files and sub-directories.

        All files will be empty.

        ```
        import os

        import seedir as sd

        r = sd.randomdir(seed=1)
        # MyFakeDir/
        # ├─churchmen.txt
        # └─exposure/

        r.realize()
        os.path.isdir('MyFakeDir/exposure')
        # True
        ```

        Parameters
        ----------
        path : str, optional
            System path where to create the folder. The default is `None`,
            in which the current working directory is used.

        Returns
        -------
        None.

        '''
        def create(f, root):
            fpath = f.get_path()
            joined = os.path.join(root, fpath)
            if isinstance(f, FakeDir):
                os.mkdir(joined)
            elif isinstance(f, FakeFile):
                with open(joined, 'w'): pass;
        if path is None:
            path = os.getcwd()
        self.walk_apply(create, root=path)

    def seedir(self, style='lines', printout=True, indent=2, uniform=None,
               anystart=None, anyend=None, depthlimit=None, itemlimit=None,
               beyond=None, first=None, sort=False, sort_reverse=False, sort_key=None,
               include_folders=None, exclude_folders=None, include_files=None,
               exclude_files=None, regex=False, mask=None,
               formatter=None, sticky_formatter=False,
               acceptable_listdir_errors=None, denied_string=' [ACCESS DENIED]', **kwargs):
        '''

        Create a folder tree diagram for `self`.  `seedir.fakedir.FakeDir` version of
        `seedir.realdir.seedir()` (see its documentation for examples).

        Parameters
        ----------
        style : 'lines', 'dash', 'arrow', 'spaces', 'plus', or 'emoji', optional
            Style to use. The default is `'lines'`.  A style determines the set
            of characters ("tokens") used to represent the base structure of
            the directory (e.g. which items belong to which folders, when items
            are the last member of a folder, etc.).  The actual tokens being used
            by each style can be viewed with `seedir.printing.get_styleargs()`.
        printout : bool, optional
            Print the folder structure in the console. The default is `True`.  When
            `False`, the folder diagram is returned as a string.
        indent : int (>= 0), optional
            Number of spaces separating items from their parent folder.
            The default is `2`.
        uniform : str or None, optional
            Characters to use for all tokens when creating the tree diagram.
            The default is `None`.  When not `None`, the extend, space, split, and
            final tokens are replaced with `uniform` (the `'spaces'` style is
            essentially `uniform = '  '`).
        anystart : str or None, optional
            Characters to append before any item (i.e. folder or file).  The
            default is `None`.  Specific starts for folders and files can be
            specified (see `**kwargs`).
        anyend : str or None, optional
            Characters to append after any item (i.e. folder or file).  The
            default is `None`.  Specific ends for folders and files can be
            specified (see `**kwargs`).
        depthlimit : int or None, optional
            Limit the depth of folders to traverse.  Folders at the `depthlimit` are
            included, but their contents are not shown (with the exception of the
            beyond parameter being specified).  The default is `None`, which can
            cause exceptionally long runtimes for deep or extensive directories.
        itemlimit : int or None, optional
            Limit the number of items in a directory to show.  Items beyond the
            `itemlimit` can be expressed using the `beyond` parameter.  The files and
            folders left out are determined by the sorting parameters
            (`sort`, `sort_reverse`, `sort_key`).  The default is `None`.
        beyond : str ('ellipsis', 'content' or a string starting with an underscore) or None, optional
            String to indicate directory contents beyond the `itemlimit` or the
            `depthlimit`.  The default is `None`.  Options are: `'ellipsis'` (`'...'`),
            `'content'` or `'contents'` (the number of files and folders beyond), or
            a string starting with `'_'` (everything after the leading underscore
            will be returned)
        first : 'files', 'folders', or None, optional
            Sort the directory so that either files or folders appear first.
            The default is `None`.
        sort : bool, optional
            Sort the directory. With no other specifications, the sort will be a
            simple alphabetical sort of the item names, but this can be altered
            with the `first`, `sort_reverse`, and `sort_key parameters`.
            The default is `False`.
        sort_reverse : bool, optional
            Reverse the sorting determined by `sort` or `sort_key`.
            The default is `False`.
        sort_key : function, optional
            Key to use for sorting file or folder names, akin to the `key` parameter
            of the builtin `sorted()` or `list.sort()`. The function should take a
            string as an argument. The default is `None`.
        include_folders, exclude_folders, include_files, exclude_files : str, list-like, or None, optional
            Folder / file names to include or exclude. The default is `None`.  By
            default, these are interpreted literally.  Pass `regex=True` for
            using regular expressions.
        regex : bool, optional
            Interpret the strings of include/exclude file/folder arguments as
            regular expressions. The default is `False`.
        mask : function, optional
            Function for filtering items.  Each individual item object
            is passed to the mask function.  If `True` is returned, the
            item is kept.  The default is `None`.
        formatter : function, optional
            Function for customizing the directory printing logic and style
            based on specific folders & files.  When passed, the formatter
            is called on each item in the file tree, and the current arguments
            are updated based what is returned.

            The formatter function should accept a FakeItem as a
            single argument (either relative or absolute, depending on what is passed
            to the `path` argument), and it should return either a dictionary or None.
            The dictionary should have names of arguments as keys and their respective
            setting as values.

            The following options can meaningfully be toggled by passing a formatter
            function: `depthlimit`, `itemlimit`, `beyond`, `first`, `sort`, `sort_reverse`,
            `sort_key`, `include_folders`, `regex`, `mask`, as well as any seedir token
            keywords (`extend`, `space`, `split`, `final`, `folderstart`, `filestart`,
            `folderend`, `fileend`).

            Note that in version 0.3.0, formatter could only be used to update
            the style tokens.  It can now be used to udpate those as well as the other
            arguments listed above.

            If None is returned by formatter, the tokens will be set by `style`.

            Note that items exlcuded by the inclusion/exclusion arguments (or the
            `mask`) *will not* be seen by formatter.  Similarly, any folder tree
            entries created by the `beyond` argument *will not* be seen by formatter.

        sticky_formatter : bool, optional
            When True, updates to argumnts made by the `formatter` (see above)
            will be permanent.  Thus, if arguments are updated when the `formatter`
            is called on a folder, its children will (recursively) inherit
            those new arguments.

        acceptable_listdir_errors : Exception, tuple, or None

            **New in v0.5.0**

            Set errors which, when raised when listing the contents of a folder,
            do not halt traversal.  This parameter was added to allow
            folders to be skipped when a `PermissionError` is raised.  For folders
            which raise an acceptable error, an additional string is added to their
            entry in the diagram (see `denied_string`).

            Providing one Exception causes only that type of Exception to be ignored.
            Multiple Exception types can be handled by passing mutple Exceptions
            as a tuple.  Pass `None` to not allow any Exceptions (in this case,
            an error is raised).

            Exception types which are not provided will still be raised.

            This parameter is mostly meaningless for FakeDir objects, except
            for testing purposes.

        denied_string : str

            **New in v0.5.0**

            String tag to signify that a folder was not able to be traversed
            due to one of the `acceptable_listdir_errors` being raised.  This
            is a string added after the folder name (and `folderend`) strings.
            The default is `" [ACCESS DENIED]"`.

        **kwargs : str
            Specific tokens to use for creating the file tree diagram.  The tokens
            use by each builtin style can be seen with `seedir.printing.get_styleargs()`.
            Valid options are `extend` (characters to show the extension of a directory
            while its children are traversed), `space` (character to provide the
            correct indentation of an item when some of its parent / grandparent
            directories are completely traversed), `split` (characters to show a
            folder or file within a directory, with more items following),
            `final` (characters to show a folder or file within a directory,
            with no more items following), `folderstart` (characters to prepend
            before any folder), `filestart` (characters to preppend before any
            file), `folderend` (characters to append after any folder), and
            `fileend` (characters to append after any file). The following shows
            the default tokens for the `'lines'` style:

                >>> import seedir as sd
                >>> sd.get_styleargs('lines')
                {'split': '├─', 'extend': '│ ', 'space': '  ', 'final': '└─', 'folderstart': '', 'filestart': '', 'folderend': '/', 'fileend': ''}

            All default style tokens are 2 character strings, except for
            the file/folder start/end tokens.  Style tokens from `**kwargs` are not
            affected by the indent parameter.  The `uniform`, `anystart`, and
            `anyend` parameters can be used to affect multiple style tokens.

        Notes
        -------

        The parameter `slash` was deprecated in 0.5.0.  Pass `folderend` as
        an additional keyword argument instead.

        Returns
        -------
        s (str) or None
            The tree diagram (as a string) or None if prinout = True, in which
            case the tree diagram is printed in the console.

        '''

        # call
        args = dict(style=style,
                    printout=printout,
                    indent=indent,
                    uniform=uniform,
                    anystart=anystart,
                    anyend=anyend,
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
                    mask=mask,
                    formatter=formatter,
                    sticky_formatter=sticky_formatter,
                    acceptable_listdir_errors=acceptable_listdir_errors,
                    denied_string=denied_string,
                    **kwargs)

        FDS = FakeDirStructure()
        return FDS(self, **args)

    def set_child_depths(self):
        '''Recursively set depths of `self` and its children.
        Called automatically when a new `parent` is assigned.'''
        def apply_setdepth(FD):
            FD.set_depth()
        self.walk_apply(apply_setdepth)

    def trim(self, depthlimit):
        """
        Remove items beyond the `depthlimit`.

        ```
        >>> import seedir as sd
        >>> r = sd.randomdir(seed=456)
        >>> r
        MyFakeDir/
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
          └─cataclysmic.txt

        >>> r.trim(1)
        >>> r
        MyFakeDir/
        ├─Vogel.txt
        ├─monkish.txt
        ├─jowly.txt
        ├─scrooge/
        ├─Uganda/
        └─pedantic/

        ```


        Parameters
        ----------
        depthlimit : non-negative int
            Files beyond this depth will be cut. The root has depth `0`.

        Raises
        ------
        ValueError
            `depthlimit` is not a non-negative int

        Returns
        -------
        None.

        """
        depthlimit = int(depthlimit)
        if depthlimit < 0:
            raise ValueError('depthlimit must be non-negative int')
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
        """
        Recursively apply a function the children of self (and so on)

        ```
        >>> import seedir as sd
        >>> r = sd.randomdir(seed=5)
        >>> r
        MyFakeDir/
        ├─senor.txt
        ├─verb.txt
        ├─takeoff.txt
        ├─monastic/
        │ ├─paddy.txt
        │ ├─ewe.txt
        │ ├─advantage.txt
        │ ├─hooves/
        │ └─registrar/
        └─zag/
          ├─thematic.txt
          ├─inelastic.txt
          ├─fierce.txt
          ├─gout/
          └─stein/
            ├─vector.txt
            ├─sora.txt
            └─proviso.txt

        >>> def replace_txt(f):
        ...    f.name = f.name.replace('txt', 'pdf')

        >>> r.walk_apply(replace_txt)
        >>> r
        MyFakeDir/
        ├─senor.pdf
        ├─verb.pdf
        ├─takeoff.pdf
        ├─monastic/
        │ ├─paddy.pdf
        │ ├─ewe.pdf
        │ ├─advantage.pdf
        │ ├─hooves/
        │ └─registrar/
        └─zag/
          ├─thematic.pdf
          ├─inelastic.pdf
          ├─fierce.pdf
          ├─gout/
          └─stein/
            ├─vector.pdf
            ├─sora.pdf
            └─proviso.pdf

        ```

        Parameters
        ----------
        foo : function
            Function to apply.
        *args :
            Additional positional arguments for `foo`.
        **kwargs :
            Additional keyword arguments for `foo`.

        Returns
        -------
        None.

        """
        foo(self, *args, **kwargs)
        for f in self._children:
            if isinstance(f, FakeDir):
                f.walk_apply(foo, *args, **kwargs)
            else:
                foo(f, *args, **kwargs)

def get_random_int(collection, seed=None):
    '''
    Helper function for selecting a random integer, used by seedir.populate().

    Parameters
    ----------
    collection : list-like
        Collection of integers to select from.
    seed : int or float, optional
        Random seed. The default is None.

    Raises
    ------
    TypeError
        Non-integer found.

    Returns
    -------
    r : int
        Randomly chosen int from collection.

    '''
    r = random.Random(seed).choice(collection)
    if not isinstance(r, int):
        raise TypeError('non int found')
    return r

def populate(fakedir, depth=3, folders=2, files=2, stopchance=.5, seed=None,
             extensions=['txt']):
    '''
    Function for populating `seedir.fakedir.FakeDir` objects with random files and folders.
    Used by `seedir.fakedir.randomdir()`.  Random dictionary names are chosen
    for file and folder names.

    Parameters
    ----------
    fakedir : seedir.fakedir.FakeDir
        Fake directory to populate.
    depth : int, optional
        Maximum depth to create folders and files. The default is `3`.
    folders : int or collection of integers, optional
        Parameter for setting the number of folders per directory.
        The default is `2`.  If `int`, represents the number of folders
        per directory.  If collection of integers, a random value will be
        chosen from the collection each time a directory is popualted.
    files : int or collection of integers, optional, optional
        Same as the folders parameter, but for files.
    stopchance : float between 0 and 1, optional
        Chance that an added folder will not be populated. The default is `.5`.
    seed : int or float, optional
        Random seed. The default is `None`.
    extensions : list-likie, optional
        Collection of extensions to randomly select from for files.  The
        default is `['txt']`.  Leading period can be included or omitted.

    Raises
    ------
    ValueError
        Issue selecting int from folders or files.

    Returns
    -------
    None, input is modified in place.

    '''
    random.seed(seed)
    if not isinstance(folders, int):
        try:
            fold_num = get_random_int(folders, seed=seed)
        except:
            raise ValueError('folders must be an int or collection of int')
    else:
        fold_num = folders
    if not isinstance(files, int):
        try:
            file_num = get_random_int(files, seed=seed)
        except:
            raise ValueError('files must be an int or collection of int')
    else:
        file_num = files
    for i in range(file_num):
        name = random.choice(words) + random.choice(extensions)
        while name in [f.name for f in fakedir._children]:
            name = random.choice(words) + random.choice(extensions)
        fakedir.create_file(name)
    for i in range(fold_num):
        name = random.choice(words)
        while name in [f.name for f in fakedir._children]:
            name = random.choice(words)
        fakedir.create_folder(name)
    for f in fakedir._children:
        if isinstance(f, FakeDir):
            if f.depth <= depth and random.uniform(0, 1) > stopchance:
                if seed is not None:
                    seed += random.random()
                populate(f, depth=depth, folders=folders, files=files,
                         seed=seed, stopchance=stopchance,
                         extensions=extensions)

def randomdir(depth=2, files=range(1,4), folders=range(0,4),
              stopchance=.5, seed=None, name='MyFakeDir', extensions=['txt']):
    '''
    Create a randomized `seedir.fakedir.FakeDir`, initialized with random
    dictionary words.

    ```
    >>> import seedir as sd
    >>> sd.randomdir(seed=7)
    MyFakeDir/
    ├─Hardin.txt
    ├─Kathleen.txt
    ├─berserk/
    └─pineapple/
      ├─visceral.txt
      ├─gestural.txt
      ├─plenty.txt
      ├─discoid/
      │ ├─eclat.txt
      │ └─milord/
      ├─Offenbach/
      │ ├─Trianon.txt
      │ ├─Monday.txt
      │ ├─ditty.txt
      │ ├─peddle/
      │ ├─delta/
      │ └─irredentism/
      └─Perseus/
        ├─hothouse.txt
        ├─clock.txt
        ├─covetous/
        └─Ekstrom/

    ```

    Parameters
    ----------
    depth : int, optional
        Maximum depth to create folders and files. The default is `3`.
    folders : int or collection of integers, optional
        Parameter for setting the number of folders per directory.
        The default is `range(1,4)`.  If `int`, represents the number of folders
        per directory.  If collection of integers, a random value will be
        chosen from the collection each time a directory is popualted.
    files : int or collection of integers, optional, optional
        Same as the `folders` parameter, but for files.  The default
        is `range(0,4)`.
    stopchance : float between 0 and 1, optional
        Chance that an added folder will not be populated. The default is `.5`.
    seed : int or float, optional
        Random seed. The default is `None`.
    extensions : list-likie, optional
        Collection of extensions to randomly select from for files.  The
        default is `['txt']`.  Leading period can be included or omitted.

    Returns
    -------
    top : seedir.fakedir.FakeDir
        Fake directory.

    '''
    top = FakeDir(name)
    new_ex = []
    for x in extensions:
        if x[0] != '.':
            new_ex.append('.' + x)
        else:
            new_ex.append(x)
    populate(top, depth, folders, files, seed=seed, stopchance=stopchance,
             extensions=new_ex)
    return top

def recursive_add_fakes(path, parent, depth=0, depthlimit=None,
                        itemlimit=None, first=None, sort=False,
                        sort_reverse=False, sort_key=None,
                        include_folders=None, exclude_folders=None,
                        include_files=None, exclude_files=None,
                        mask=None, regex=False):
    '''
    Recursive helper function for seedir.fakedir(), for creating a
    fake folder tree from a real one.

    Parameters
    ----------
    path : str
        System path of a folder.
    parent : seedir.fakedir.FakeDir
        Fake directory to add items to.
    depth : int, optional
        Tracker for depth of folders traversed. The default is 0.
    depthlimit : int, optional
        Limit on the depth of folders to traverse. The default is None.
    itemlimit : int, optional
        Limit on the number of items to include per directory.
        The default is None.
    first : 'folders' or 'files', optional
        Sort to have folders or files appear first. The default is None.
    sort : bool, optional
        Apply a sort to items in each directory. The default is False.
    sort_reverse : bool, optional
        Reverse the sort. The default is False.
    sort_key : function, optional
        Key function for sorting item names. The default is None.
    include_folders, exclude_folders, include_files, exclude_files : str, list-like, or None, optional
            Folder / file names to include or exclude. The default is None.
    mask : function, optional
        Function for filtering items.  Absolute paths of each individual item
        are passed to the mask function.  If True is returned, the
        item is kept.  The default is None.
    regex : bool, optional
        Interpret include/exclude folder/file arguments as regular
        expressions. The default is False.

    Returns
    -------
    None.

    '''
    RDS = RealDirStructure()
    if depthlimit is not None and depth >= depthlimit:
        return
    depth +=1
    listdir = listdir_fullpath(path)
    if sort or first is not None:
        listdir = RDS.sort_dir(listdir, first=first,
                               sort_reverse=sort_reverse, sort_key=sort_key)
    if any(arg is not None for arg in [
            include_folders,
            exclude_folders,
            include_files,
            exclude_files,
            mask]):
        listdir = RDS.filter_items(listdir,
                                   include_folders=include_folders,
                                   exclude_folders=exclude_folders,
                                   include_files=include_files,
                                   exclude_files=exclude_files,
                                   regex=regex,
                                   mask=mask)
    for i, f in enumerate(listdir):
        name = os.path.basename(f)
        if i == itemlimit:
            break
        if os.path.isdir(f):
            new = FakeDir(name=name, parent=parent)
            recursive_add_fakes(path=f, parent=new, depth=depth,
                                depthlimit=depthlimit,
                                itemlimit=itemlimit,
                                include_folders=include_folders,
                                exclude_folders=exclude_folders,
                                include_files=include_files,
                                exclude_files=exclude_files,
                                mask=mask, regex=regex)
        else:
            new = FakeFile(name=name, parent=parent)

def fakedir(path, depthlimit=None, itemlimit=None, first=None,
            sort=False, sort_reverse=False, sort_key=None,
            include_folders=None, exclude_folders=None, include_files=None,
            exclude_files=None, mask=None, regex=True):
    '''
    Function for creating a `seedir.fakedir.FakeDir` (representation of a directory)
    from a real system directory.  Rather than immediately representing
    a directory as a string (`seedir.realdir.seedir()`), this function can be used
    to create an editable representation of the directory, or to join one or
    more directories.

    ```
    >>> import seedir as sd
    >>> f = sd.fakedir('.', depthlimit=0)
    >>> type(f)
    <class 'seedir.fakedir.FakeDir'>

    ```

    Parameters
    ----------
    path : str
        System path of a directory.
    depthlimit : int, optional
        Limit on the depth of directories to traverse. Folders at the depth
        limit will be included, but their contents will not be.
        The default is `None`.
    itemlimit : int, optional
        Limit on the number of items to include per directory.
        The default is `None`, meaning all items will be added.  The priority
        of items is determined by `os.listdir()`, unless sorting arguments
        are passed.
    first : 'folders' or 'files', optional
        Sort to show folders or files first. The default is `None`.
    sort : bool, optional
        Apply a (name) sort on each directory. The default is `False`.
    sort_reverse : bool, optional
        Reverse the sort. The default is `False`.
    sort_key : function, optional
        Key function for sorting the file names. The default is `None`.
    include_folders, exclude_folders, include_files, exclude_files : str, list-like, or None, optional
            Folder / file names to include or exclude. The default is `None`.
    mask : function, optional
        Function for filtering items.  Absolute paths of each individual item
        are passed to the mask function.  If `True` is returned, the
        item is kept.  The default is `None`.
    regex : bool, optional
        Interpret include/exclude folder/file arguments as regular
        expressions. The default is `False`.

    Raises
    ------
    FakedirError
        path does not point to a directory.

    Returns
    -------
    output : seedir.fakedir.FakeDir
        Fake directory matching the path.

    '''
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
                        exclude_files=exclude_files,
                        mask=mask, regex=regex)
    return output

def fakedir_fromstring(s, start_chars=None, name_chars=None,
                       header_regex=None, name_regex=None,
                       supername='FakeDir', parse_comments=True):
    '''
    Convert a string folder tree diagram into a `seedir.fakedir.FakeDir`.
    This can be used to read in external representations of folder structures,
    edit them, and recreate them in a new location.

    This function has mostly been tested with examples from Stack Overflow
    and other Python learning sites (as well as output from `seedir.realdir.seedir()`).
    There are surely cases which will causes errors or unexpected results.

    ```
    >>> import seedir as sd
    >>> s = """doc/
    ... ├─_static/
    ... │ ├─embedded/
    ... │ │ ├─deep_file
    ... │ │ └─very/
    ... │ │   └─deep/
    ... │ │     └─folder/
    ... │ │       └─very_deep_file
    ... │ └─less_deep_file
    ... ├─about.rst
    ... ├─conf.py
    ... └─index.rst"""

    >>> f = sd.fakedir_fromstring(s) # now can be edited or restyled
    >>> f.seedir(style='spaces')
    doc/
      _static/
        embedded/
          deep_file
          very/
            deep/
              folder/
                very_deep_file
        less_deep_file
      about.rst
      conf.py
      index.rst

    ```


    Parameters
    ----------
    s : str
        String representation a folder tree.
    start_chars : str, optional
        A string of characters which will be searched for as the start
        of a folder or file name. The default is `None`, in which case the
        characters are all letters, numbers, and punctuation marks except
        for `/:?"*<>|` or `+=-`.
    name_chars : str, optional
        A string of characters which will be searched for as being part
        of a file or folder name. The default is `None`, in which case the
        characters are all letters, numbers, punctuation marks except
        for `/:?"*<>|,` and spaces.
    header_regex : str, optional
        Regular expression to match the "header" of each line, i.e. the
        structural characters of the folder diagram.  The default is `None`.
        If passed, the `start_chars` argument will be ignored.  This and
        `name_regex` are intended to provide functionality for parsing
        specific or unusual cases.
    name_regex : str, optional
        Regular expression to match all the folder or file names.
        The default is `None`.
        If passed, the `start_chars` argument will be ignored.
    supername : str, optional
        Name to give the head directory if one cannot be found.
        The default is `'FakeDir'`.  This can happen when there is no clear
        head directory in the string.
    parse_comments : bool, optional
        Try to parse and remove Python comments (following `#`).
        The default is `True`.

    Returns
    -------
    seedir.fakedir.FakeDir
        Fake directory corresponding to the input string.

    '''
    slashes = ['/', '\\', os.sep]
    joinedslashes = ''.join(slashes)

    byline = s.split('\n')
    keyboard_chars = (string.ascii_letters + string.digits
                      + string.punctuation)
    filtered = "".join([c for c in keyboard_chars if c not in '/:?"*<>|'])
    if start_chars is None:
        start_chars = "".join([c for c in filtered if c not in '+=-'])
    if name_chars is None:
        name_chars = filtered + ' ' + '-'

    names = []
    headers = []
    depths = []

    for line in byline:
        if not line:
            continue
        if header_regex is None:
            header = re.match('.*?(?=[{}])'.format(start_chars), line)
        else:
            header = re.match(header_regex, line)
        if header is None:
            continue
        else:
            header = header.group()
        depth = len(header)
        if name_regex is None:
            name = re.match('[{}]*[/\\\\]*'.format(name_chars), line[depth:])
        else:
            name = re.match(name_regex, line)
        if name is None:
            continue
        else:
            name = name.group()
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
        if name.strip()[-1] in slashes:
            is_folder = True
        if i < len(names) - 1:
            if depths[i + 1] > depths[i]:
                is_folder = True

        fmt_name = name.rstrip(joinedslashes)

        if depths[i] == min_depth:
            if is_folder:
                fakeitems.append(FakeDir(fmt_name, parent=superparent))
            else:
                fakeitems.append(FakeFile(fmt_name, parent=superparent))
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
                fakeitems.append(FakeDir(fmt_name, parent=parent))
            else:
                fakeitems.append(FakeFile(fmt_name, parent=parent))

    if superparent is not None:
        return superparent
    else:
        idx = depths.index(min_depth)
        return fakeitems[idx]

