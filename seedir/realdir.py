# -*- coding: utf-8 -*-

# Note: this module fails doctesting

"""
This module provides code for producing folder structure strings for directories.
Currently, the only tool here is `seedir()`, the primary function of the
package `seedir`.  This returns or prints the folder structure for a given path.
The main algorithm for determining the folder structure string is within the
<code>seedir.folderstructure.FolderStructure</code> class.
"""

import os

from seedir.folderstructure import RealDirStructure

from seedir.errors import SeedirError

import seedir.printing as printing


def seedir(path=None, style='lines', printout=True, indent=2, uniform=None,
           anystart=None, depthlimit=None, itemlimit=None, beyond=None,
           first=None, sort=False, sort_reverse=False, sort_key=None,
           include_folders=None, exclude_folders=None, include_files=None,
           exclude_files=None, regex=False, mask=None, formatter=None,
           sticky_formatter=False, slash='/', **kwargs):
    '''

    Primary function of the seedir package: generate folder trees for
    computer directories.

    ## EXAMPLES

    ```
    >>> import seedir as sd

    ```

    Make a basic tree diagram:

    ```
    >>> c = 'example/folder/path'
    >>> sd.seedir(c)
    doc/
    ├─_static/
    │ ├─embedded/
    │ │ ├─deep_file
    │ │ └─very/
    │ │   └─deep/
    │ │     └─folder/
    │ │       └─very_deep_file
    │ └─less_deep_file
    ├─about.rst
    ├─conf.py
    └─index.rst

    ```

    Select different styles for the tree:

    ```
    >>> sd.seedir(c, style='dash')
    doc/
    |-_static/
    | |-embedded/
    | | |-deep_file
    | | |-very/
    | |   |-deep/
    | |     |-folder/
    | |       |-very_deep_file
    | |-less_deep_file
    |-about.rst
    |-conf.py
    |-index.rst

    ```

    Sort the folder contents, separting folders and files:

    ```
    >>> sd.seedir(c, sort=True, first='files')
    doc/
    ├─about.rst
    ├─conf.py
    ├─index.rst
    └─_static/
      ├─less_deep_file
      └─embedded/
        ├─deep_file
        └─very/
          └─deep/
            └─folder/
              └─very_deep_file

    ```

    Limit the folder depth or items included:

    ```
    >>> sd.seedir(c, depthlimit=2, itemlimit=1)
    doc/
    ├─_static/
    │ ├─embedded/
    │ └─less_deep_file
    └─about.rst

    ```

    Include or exclude specific items (with or without regular expressions):

    ```
    >>> sd.seedir(c, exclude_folders='_static')
    doc/
    ├─about.rst
    ├─conf.py
    └─index.rst

    ```

    Parameters
    ----------
    path : str or None, optional
        System path of a directory.  If None, current working directory is
        used.
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
    beyond : str ('ellipsis', 'cotent' or a string starting with an underscore) or None, optional
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
        Folder / file names to include or exclude. The default is `None`.
    regex : bool, optional
        Interpret the strings of include/exclude file/folder arguments as
        regular expressions. The default is `False`.
    mask : function, optional
        Function for filtering items.  Absolute paths of each individual item
        are passed to the `mask` function.  If `True` is returned, the
        item is kept.  The default is `None`.
    formatter : function, optional
        Function for customizing the tokens used for specific items during
        traversal.

        The formatter function should accept a system path as a
        single argument (either relative or absolute, depending on what is passed
        to the `path` argument), and it should return either a dictionary or None.
        The dictionary should have names of seedir tokens as keys ('split',
        'extend', 'space', 'final', 'folderstart', or 'finalstart') and strings
        to use for those tokens as values.  Call `seedir.printing.get_styleargs()`
        for examples.  Though note, not all six tokens need to be specified.

        If None is returned by formatter, the tokens will be set by `style`.

        Note that items exlcuded by the inclusion/exclusion arguments (or the
        `mask`) *will not* be seen by formatter.  Alternatively, any folder tree
        entries created by the `beyond` argument *will* be seen by formatter.

    slash : str, option:
        Slash character to follow folders.  If `'sep'`, uses `os.sep`.  The
        default is `'/'`.
    **kwargs : str
        Specific tokens to use for creating the file tree diagram.  The tokens
        use by each builtin style can be seen with `seedir.printing.get_styleargs()`.
        Valid options are `extend` (characters to show the extension of a directory
        while its children are traversed), `space` (character to provide the
        correct indentation of an item when some of its parent / grandparent
        directories are completely traversed), `split` (characters to show a
        folder or file within a directory, with more items following),
        `final` (characters to show a folder or file within a directory,
        with no more items following), `folderstart` (characters to append
        before any folder), and `filestart` (characters to append beffore any
        file).  The following shows the default tokens for the `'lines'` style:

            >>> import seedir as sd
            >>> sd.get_styleargs('lines')
            {'split': '├─', 'extend': '│ ', 'space': '  ', 'final': '└─', 'folderstart': '', 'filestart': ''}

        All default style tokens are 2 character strings, except for
        `folderstart` and `filestart`.  Style tokens from `**kwargs` are not
        affected by the indent parameter.  The `uniform` and `anystart`
        parameters can be used to affect multiple style tokens.

    Raises
    ------
    SeedirError
        Improperly formatted arguments.

    Returns
    -------
    s (str) or None
        The tree diagram (as a string) or `None` if `prinout = True`, in which
        case the tree diagram is printed in the console.

    '''

    accept_kwargs = ['extend', 'split', 'space', 'final',
                     'folderstart', 'filestart']

    if any(i not in accept_kwargs for i in kwargs.keys()):
        raise SeedirError('kwargs must be any of {}'.format(accept_kwargs))

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

    if path is None:
        path = os.getcwd()

    base_args = dict(depthlimit=depthlimit,
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
                     mask=mask,
                     formatter=formatter,
                     sticky_formatter=sticky_formatter,
                     **styleargs)

    s = RealDirStructure(path,
                         base_args=base_args,
                         **base_args,)

    if printout:
        print(s)
    else:
        return s