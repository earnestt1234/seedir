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
import pathlib

from seedir.folderstructure import PathlibStructure, RealDirStructure

def _parse_path(path):
    '''Helper function added to parse the input to `seedir.realdir.seedir()`.
    Detects strings (paths) or pathlib objects.'''

    if isinstance(path, str):
        path = os.path.abspath(os.path.expanduser(path))
    elif isinstance(path, pathlib.Path):
        path = path.expanduser().resolve()
    else:
        raise TypeError(f"Can only parse str or pathlib.Path, not {type(path)}.")

    return path

def seedir(path=None, style='lines', printout=True, indent=2, uniform=None,
           anystart=None, anyend=None, depthlimit=None, itemlimit=None,
           beyond=None, first=None, sort=False, sort_reverse=False,
           sort_key=None, include_folders=None, exclude_folders=None,
           include_files=None, exclude_files=None, regex=False, mask=None,
           formatter=None, sticky_formatter=False,
           acceptable_listdir_errors=PermissionError,
           denied_string=' [ACCESS DENIED]', **kwargs):
    '''

    Primary function of the seedir package: generate folder trees for
    computer directories.

    ## EXAMPLES

    ```
    >>> import seedir as sd

    ```

    Make a basic tree diagram:

    ```
    >>> c = 'path/to/doc'
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
    path : str, pathlib.Path, or None, optional
        System path of a directory.  If None, current working directory is
        used.  The path can be either a string path or a pathlib object.
        In both cases, the path is converted to an absolute path, and the
        tilde (~) is expanded.
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
        Characters to prepend before any item (i.e. folder or file).  The
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
        Function for filtering items.  Absolute paths of each individual item
        are passed to the `mask` function.  If `True` is returned, the
        item is kept.  The default is `None`.  The type of the object
        passed to `mask` corresponds with that passed as input:
        `str` or `pathlib.Path`.
    formatter : function, optional
        Function for customizing the directory printing logic and style
        based on specific folders & files.  When passed, the formatter
        is called on each item in the file tree, and the current arguments
        are updated based what is returned.

        The formatter function should accept a system path as a
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

        The type of the object passed to `formatter` corresponds with that
        passed as input: `str` or `pathlib.Path`.

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

        The default is `PermissionError`, which will skip folders
        for which the caller does not have permissions to access.

    denied_string : str

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
        The tree diagram (as a string) or `None` if `prinout = True`, in which
        case the tree diagram is printed in the console.

    '''

    if path is None:
        path = os.getcwd()

    path = _parse_path(path)

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

    structure = PathlibStructure() if isinstance(path, pathlib.Path) else RealDirStructure()

    return structure(path, **args)
