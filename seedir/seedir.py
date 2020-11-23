# -*- coding: utf-8 -*-
"""
This module provides code for producing folder structure strings for folders
of the user's computer.  The main tool here is seedir() (seedir.seedir()),
which takes a file path and produces a folder diagram.   The other functions
are mostly helpers for seedir().

@author: Tom Earnest

GitHub: https://github.com/earnestt1234/seedir
"""
__pdoc__ = {}

for key in ['count_files',
            'count_folders',
            'sort_dir',
            'beyond_depth_str',
            'get_base_header',
            'filter_item_names']:
    __pdoc__[key] = False

import os

import natsort

from seedir.errors import SeedirError
import seedir.printing as printing

def count_files(paths):
    '''
    Count the number of files in a collection of paths.

    Parameters
    ----------
    paths : list-like
        Collection of system paths.

    Returns
    -------
    files : int
        Count of files.

    '''
    files = sum([os.path.isfile(p) for p in paths])
    return files

def count_folders(paths):
    '''
    Count the number of folders in a collection of paths.

    Parameters
    ----------
    paths : list-like
        Collection of system paths.

    Returns
    -------
    files : int
        Count of folders.

    '''
    folders = sum([os.path.isdir(p) for p in paths])
    return folders

def sort_dir(names, root='', first=None, sort_reverse=False, sort_key=None):
    '''
    Sorting function used by seedir.seedir() to sort contents when
    producing folder diagrams.

    Parameters
    ----------
    names : list-like
        Collection of file or folder names (without the root).
    root : str, optional
        Full path of the parent directory of the elements of names.
        The default is '', which allows sorting without checking if
        names passed correspond to files or folders.
    first : 'files' or 'folders', optional
        Sort either files or folders first. The default is None.
    sort_reverse : bool, optional
        Reverse the sort applied. The default is False.
    sort_key : function, optional
        Function to apply to sort the names passed. The function should
        take a string as an argument.  The default is None.

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
    if root == '' and first is not None:
        raise SeedirError('must pass a root when including first')
    if first in ['folders', 'files']:
        folders = [p for p in names if
                   os.path.isdir(os.path.join(root, p))]
        files = [p for p in names if not
                 os.path.isdir(os.path.join(root, p))]
        folders = natsort.natsorted(folders, reverse=sort_reverse,
                                    key=sort_key)
        files = natsort.natsorted(files, reverse=sort_reverse, key=sort_key)
        return folders + files if first == 'folders' else files + folders
    else:
        return list(natsort.natsorted(names,
                                      reverse=sort_reverse,
                                      key=sort_key))

def beyond_depth_str(beyond, paths=None):
    '''
    Generates the text for seedir.seedir() when using the 'beyond'
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
    paths : collection of file paths, optional
        System paths of the items beyond the limit, used when the 'beyond'
        argeument is 'content' or 'contents'. The default is None.

    Raises
    ------
    SeedirError
        Raised when the 'beyond' argument is not recognized.

    Returns
    -------
    str
        String indicating what lies beyond

    '''
    if beyond.lower() == 'ellipsis':
        return '...'
    elif beyond.lower() in ['contents','content']:
        folders = count_folders(paths)
        files = count_files(paths)
        return '{} folder(s), {} file(s)'.format(folders, files)
    elif beyond and beyond[0] == '_':
        return beyond[1:]
    else:
        s1 = '"beyond" must be "ellipsis", "content", or '
        s2 = 'a string starting with "_"'
        raise SeedirError(s1 + s2)

def get_base_header(incomplete, extend, space):
    '''
    For seedir.seedir(), generate the combination of extend and space
    tokens to prepend to file names when generating folder diagrams.
    See the documentation for seedir.seedir() for an
    explanation of these tokens.

    The string generated here will still be missing the branch token
    (split or final) as well as any folderstart or filestart tokens.
    They are added within seedir.seedir().

    For any item included in a folder diagram, the combination of
    extend and space tokens is based on the depth of the item as well as the
    parent folders to that item which are not completed.  This information
    is symbolized with the `incomplete` argument.  The following illustrates
    the incomplete arguments passed to this function for an example folder
    tree:

        >>> #

        doc/
        ├─_static/                  [0]
        │ ├─embedded/               [0, 1]
        │ │ ├─deep_file             [0, 1, 2]
        │ │ └─very/                 [0, 1, 2]
        │ │   └─deep/               [0, 1, 3]
        │ │     └─folder/           [0, 1, 4]
        │ │       └─very_deep_file  [0, 1, 5]
        │ └─less_deep_file          [0, 1]
        └─index.rst                 [0]

    Parameters
    ----------
    incomplete : list-like
        List of integers denoting the depth of incomplete folders at the time
        of constructing the line for a given item.  Zero represents being
        inside the main folder, with increasing integers meaing increasing
        depth.
    extend : str
        Characters symbolizing the extension of a folder.
    space : str
        Characters providing the gap between items and earlier parents.

    Returns
    -------
    str
        Base header string.

    '''
    base_header = []
    max_i = max(incomplete)
    for p in range(max_i):
        if p in incomplete:
            base_header.append(extend)
        else:
            base_header.append(space)
    return "".join(base_header)

def filter_item_names(root, listdir, include_folders=None,
                      exclude_folders=None, include_files=None,
                      exclude_files=None, regex=False,
                      mask=None):
    '''
    Filter for folder and file names in seedir.seedir().  Removes or includes
    items matching filtering strings.

    Parameters
    ----------
    root : str
        The root path of the items in the listdir arguemnt.
    listdir : list-like
        Collection of file or folder names, under the directory named in the
        root argument.
    include_folders : str or list-like, optional
        Folder names to include. The default is None.
    exclude_folders : str or list-like, optional
        Folder names to exclude. The default is None.
    include_files : str or list-like, optional
        File names to include. The default is None.
    exclude_files : str or list-like, optional
        File names to exclude. The default is None.
    regex : bool, optional
        Interpret strings as regular expressions. The default is False.
    mask : function, optional
        Function for filtering items.  Absolute paths of each individual item
        are passed to the mask function.  If True is returned, the
        item is kept.  The default is None.

    Raises
    ------
    SeedirError
        When the exlcusion or inclusion arguments are not strings or
        iterables.

    Returns
    -------
    keep : list
        Filtered input.

    '''
    keep = []
    for l in listdir:
        sub = os.path.join(root, l)

        if mask is not None:
            if mask(sub) is not True:
                continue

        if os.path.isdir(sub):
            if isinstance(include_folders, str):
                if not printing.is_match(include_folders, l, regex):
                    continue
            elif include_folders is not None:
                try:
                    if not any(printing.is_match(n, l, regex)
                               for n in include_folders):
                        continue
                except:
                    raise SeedirError('Failure when trying to iterate '
                                      'over "include_folders" and '
                                      'match strings')
            if isinstance(exclude_folders, str):
                if printing.is_match(exclude_folders, l, regex):
                    continue
            elif exclude_folders is not None:
                try:
                    if any(printing.is_match(x, l, regex)
                           for x in exclude_folders):
                        continue
                except:
                    raise SeedirError('Failure when trying to iterate '
                                      'over "exclude_folders" and '
                                      'match strings')

        else:
            if isinstance(include_files, str):
                if not printing.is_match(include_files, l, regex):
                    continue
            elif include_files is not None:
                try:
                    if not any(printing.is_match(n, l, regex)
                               for n in include_files):
                        continue
                except:
                    raise SeedirError('Failure when trying to iterate '
                                      'over "include_files" and '
                                      'match strings')
            if isinstance(exclude_files, str):
                if printing.is_match(exclude_files, l, regex):
                    continue
            elif exclude_files is not None:
                try:
                    if any(printing.is_match(x, l, regex)
                           for x in exclude_files):
                        continue
                except:
                    raise SeedirError('Failure when trying to iterate '
                                      'over "exclude_files" and '
                                      'match strings')
        keep.append(l)
    return keep

def recursive_folder_structure(path, depth=0, incomplete=None, extend='│ ',
                               space='  ', split='├─', final='└─',
                               filestart='', folderstart='', depthlimit=None,
                               itemlimit=None, beyond=None, first=None,
                               sort=True, sort_reverse=False, sort_key=None,
                               include_folders=None, exclude_folders=None,
                               include_files=None, exclude_files=None,
                               regex=False, mask=None, slash='/'):
    '''
    Recursive function for generating folder structures.  Main tool for
    building output generated by seedir.seedir().

    Parameters
    ----------
    path : str
        File path.
    depth : int, optional
        Integer denoting the current folder depth. Starts at 0.
    incomplete : list-like, optional
        List of incomplete folder depths, passed to seedir.get_base_header().
        The default is None.
    extend : str, optional
        Token to denote a folder has more children below. The default is '│ '.
    space : str, optional
        Token to space items out to the correct depth. The default is '  '.
    split : str, optional
        Token before file/folder when there are more items in the directory
        below it. The default is '├─'.
    final : str, optional
        Token before the last file/folder in a directory. The default is '└─'.
    filestart : str, optional
        String to prepend to file names. The default is ''.
    folderstart : TYPE, optional
        String to prepend to folder names. The default is ''.
    depthlimit : int, optional
        Limit on how many folders deep to traverse. The default is None.
    itemlimit : int, optional
        Limit on how many items to show for a directory. The default is None.
    beyond : str, optional
        Method to denote items beyond the depthlimit or itemlimit.
        The default is None.  Options are:
            - 'ellipsis' ('...')
            - 'content' or 'contents' (the number of files and folders beyond)
            - a string starting with '_' (everything after the leading
              underscore will be returned)
    first : 'folders' or 'files', optional
        Show folders first for files first. The default is None.
    sort : bool, optional
        Sort directories being diagrammed. The default is True.
    sort_reverse : bool, optional
        Reverse the sort. The default is False.
    sort_key : function, optional
        Key function used for sorting item names. The default is None.
    include_folders, exclude_folders, include_files, exclude_files : str or list-like, optional
        Folder / file names to include or exclude. The default is None.
    regex : bool, optional
        Interpret include/exclude file/folder arguments as
        regular expressions. The default is False.
    mask : function, optional
        Function for filtering items.  Absolute paths of each individual item
        are passed to the mask function.  If True is returned, the
        item is kept.  The default is None.
    slash : str, option:
        Slash character to follow folders.  If 'sep', uses os.sep.  The
        default is '/'.

    Returns
    -------
    output : str
        Folder tree diagram.

    '''
    # initialize
    output = ''
    if incomplete is None:
        incomplete = []
    if depth == 0:
        output += folderstart + os.path.basename(path) + slash +'\n'

    # stop when too deep
    if depth == depthlimit and beyond is None:
        return output

    # enter folder, increase depth
    listdir = os.listdir(path)
    incomplete.append(depth)
    depth += 1

    # if depth passed limit, return with "beyond" added
    if depthlimit and depth > depthlimit:
        paths = [os.path.join(path, item) for item in listdir]
        extra = beyond_depth_str(beyond, paths)
        if beyond is not None and extra:
            base_header = get_base_header(incomplete, extend, space)
            output += base_header + final + extra + '\n'
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
        incomplete = [n for n in incomplete if n < depth]
        return output

    # sort and trim the contents of listdir
    if sort or first is not None:
        listdir = sort_dir(names=listdir, root=path, first=first,
                           sort_reverse=sort_reverse, sort_key=sort_key)
    if any(arg is not None for arg in [
            include_folders,
            exclude_folders,
            include_files,
            exclude_files,
            mask]):
        listdir = filter_item_names(path, listdir,
                                    include_folders=include_folders,
                                    exclude_folders=exclude_folders,
                                    include_files=include_files,
                                    exclude_files=exclude_files,
                                    regex=regex,
                                    mask=mask)
    if not listdir:
        if depth - 1 in incomplete:
            incomplete.remove(depth-1) # remove from incomplete if empty

    # get output for each item in folder
    for i, f in enumerate(listdir):

        #if passed itemlimit, return with "beyond" added
        if i == itemlimit:
            paths = [os.path.join(path, rem) for rem in listdir[i:]]
            if beyond is not None:
                extra = beyond_depth_str(beyond, paths)
                output += base_header + final + extra + '\n'
            if depth - 1 in incomplete:
                incomplete.remove(depth-1)
            return output

        # create header for the item
        sub = os.path.join(path, f)
        base_header = get_base_header(incomplete, extend, space)
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

        # concat to output and recurse if item is folder
        if os.path.isdir(sub):
            output += header + folderstart + f + slash +'\n'
            output += recursive_folder_structure(sub, depth=depth,
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
                                                 mask=mask,
                                                 slash=slash)

        # only concat to output if file
        else:
            output += header + filestart + f + '\n'
    return output

def seedir(path=None, style='lines', printout=True, indent=2, uniform=None,
           anystart=None, depthlimit=None, itemlimit=None, beyond=None,
           first=None, sort=False, sort_reverse=False, sort_key=None,
           include_folders=None, exclude_folders=None, include_files=None,
           exclude_files=None, regex=False, mask=None, slash='/', **kwargs):
    '''

    Primary function of the seedir package: generate folder trees for
    computer directories.  seedir() is a convenience function, wrapping
    seedir.seedir.recursive_folder_structure().

    EXAMPLES:

        >>> import seedir as sd

    Make a basic tree diagram:

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

    Select different styles for the tree:

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

    Sort the folder contents, separting folders and files:

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

    Limit the folder depth or items included:

        >>> sd.seedir(c, depthlimit=2, itemlimit=1)

        doc/
        ├─_static/
        │ ├─embedded/
        │ └─less_deep_file
        └─about.rst

    Include or exclude specific items (with or without regular expressions):

        >>> sd.seedir(c, exclude_folders='_static')

        doc/
        ├─about.rst
        ├─conf.py
        └─index.rst

    Parameters
    ----------
    path : str or None, optional
        System path of a directory.  If None, current working directory is
        used.
    style : 'lines', 'dash', 'arrow', 'spaces', 'plus', or 'emoji', optional
        Style to use. The default is 'lines'.  A style determines the set
        of characters ("tokens") used to represent the base structure of
        the directory (e.g. which items belong to which folders, when items
        are the last member of a folder, etc.).  The actual tokens being used
        by each style can be viewed with seedir.get_styleargs().
    printout : bool, optional
        Print the folder structure in the console. The default is True.  When
        false, the folder diagram is returned as a string.
    indent : int (>= 0), optional
        Number of spaces separating items from their parent folder.
        The default is 2.
    uniform : str or None, optional
        Characters to use for all tokens when creating the tree diagram.
        The default is None.  When not None, the extend, space, split, and
        final tokens are replaced with uniform (the 'spaces' style is
        essentially uniform = '  ').
    anystart : str or None, optional
        Characters to append before any item (i.e. folder or file).  The
        default is None.  Specific starts for folders and files can be
        specified (see **kwargs).
    depthlimit : int or None, optional
        Limit the depth of folders to traverse.  Folders at the depthlimit are
        included, but their contents are not shown (with the exception of the
        beyond parameter being specified).  The default is None, which can
        cause exceptionally long runtimes for deep or extensive directories.
    itemlimit : int or None, optional
        Limit the number of items in a directory to show.  Items beyond the
        itemlimit can be expressed using the beyond parameter.  The files and
        folders left out are determined by the sorting parameters of seedir()
        (sort, sort_reverse, sort_key).  The default is None.
    beyond : str ('ellipsis', 'cotent' or a string starting with an
             underscore) or None, optional
        String to indicate directory contents beyond the itemlimit or the
        depthlimit.  The default is None.  Options are:
            - 'ellipsis' ('...')
            - 'content' or 'contents' (the number of files and folders beyond)
            - a string starting with '_' (everything after the leading
              underscore will be returned)
    first : 'files', 'folders', or None, optional
        Sort the directory so that either files or folders appear first.
        The default is None.
    sort : bool, optional
        Sort the directory. With no other specifications, the sort will be a
        simple alphabetical sort of the item names, but this can be altered
        with the first, sort_reverse, and sort_key parameters.
        The default is False.
    sort_reverse : bool, optional
        Reverse the sorting determined by sort or sort_key.
        The default is False.
    sort_key : function, optional
        Key to use for sorting file or folder names, akin to the key parameter
        of the builtin sorted() or list.sort(). The function should take a
        string as an argument. The default is None.
    include_folders, exclude_folders, include_files, exclude_files : str, list-like, or None, optional
        Folder / file names to include or exclude. The default is None.
    regex : bool, optional
        Interpret the strings of include/exclude file/folder arguments as
        regular expressions. The default is False.
    mask : function, optional
        Function for filtering items.  Absolute paths of each individual item
        are passed to the mask function.  If True is returned, the
        item is kept.  The default is None.
    slash : str, option:
        Slash character to follow folders.  If 'sep', uses os.sep.  The
        default is '/'.
    **kwargs : str
        Specific tokens to use for creating the file tree diagram.  The tokens
        use by each builtin style can be seen with sd.get_styleargs().  Valid
        options are (with the example token for the 'lines' style):
            - extend ('│ '): characters to show the extension of a directory
            while its children are traversed
            - space ('  '): character to provide the correct indentation
            of an item when some of its parent / grandparent directories
            are completely traversed
            - split ('├─'): characters to show a folder or file within
            a directory (with more items following)
            - final ('└─'): characters to show a folder or file within
            a directory (with no more items following)
            - folderstart (''): characters to append before any folder
            - filestart (''): characters to append beffore any file
        All default style tokens are 2 character strings.  Style tokens
        from **kwargs are not affected by the indent parameter.  The uniform
        and anystart parameters can be used to affect multiple style tokens.

    Raises
    ------
    SeedirError
        Improperly formatted arguments.

    Returns
    -------
    rfs (str) or None
        The tree diagram (as a string) or None if prinout = True, in which
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
    rfs =  recursive_folder_structure(path,
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
                                      mask=mask,
                                      **styleargs).strip()
    if printout:
        print(rfs)
    else:
        return rfs
