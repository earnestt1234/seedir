# -*- coding: utf-8 -*-
"""
Created on Wed May 19 10:29:16 2021

@author: earne
"""
import os

import natsort

from seedir.errors import SeedirError, FakedirError
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
    files = sum([p.isfile() for p in objs])
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
    folders = sum([p.isdir() for p in objs])
    return folders

def listdir_fullpath(path):
    return [os.path.join(path, f) for f in os.listdir(path)]

def sort_dir(items, first=None, sort_reverse=False, sort_key=None):
    if sort_key is None:
        key = lambda x : os.path.basename(x)
    else:
        key = lambda x: sort_key(os.path.basename(x))

    if first in ['folders', 'files']:
        folders = [p for p in items if os.path.isdir(p)]
        files = [p for p in items if not os.path.isdir(p)]
        folders = natsort.natsorted(folders, reverse=sort_reverse, key=key)
        files = natsort.natsorted(files, reverse=sort_reverse, key=key)
        return folders + files if first == 'folders' else files + folders
    else:
        return list(natsort.natsorted(items,
                                      reverse=sort_reverse,
                                      key=key))

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
        key = lambda f : f.name
    else:
        key = lambda f : sort_key(f.name)
    if first in ['folders', 'files']:
        folders = [o for o in objs if o.isdir()]
        files = [o for o in objs if o.isfile()]
        folders = natsort.natsorted(folders, reverse=sort_reverse,
                                    key=key)
        files = natsort.natsorted(files, reverse=sort_reverse, key=key)
        return folders + files if first == 'folders' else files + folders
    else:
        return natsort.natsorted(objs, reverse=sort_reverse, key=key)

def beyond_depth_str(paths, beyond):
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

def beyond_fakedepth_str(objs, beyond):
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

def filter_item_names(items, include_folders=None,
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
    for path in items:
        l = os.path.basename(path)

        if mask is not None:
            if mask(path) is not True:
                continue

        if os.path.isdir(path):
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
        keep.append(path)
    return keep

def filter_fakeitem_names(listdir, include_folders=None,
                          exclude_folders=None, include_files=None,
                          exclude_files=None, regex=False, mask=None):
    '''
    Filter for folder and file names in seedir.FakeDir.seedir().  Removes or
    includes items matching filtering strings.

    Parameters
    ----------
    listdir : list-like
        Collection of FakeDir and FakeFile objects
    include_folders : str or list-like, optional
        Folder names to include. The default is None.
    exclude_folders : str or list-like, optional
        Folder names to exclude. The default is None.
    include_files : str or list-like, optional
        File names to include. The default is None.
    exclude_files : str or list-like, optional
        File names to exclude. The default is None.
    mask : function, optional
        Function for filtering items.  Each individual item object
        are passed to the mask function.  If True is returned, the
        item is kept.  The default is None.
    regex : bool, optional
        Interpret strings as regular expressions. The default is False.

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
        if mask is not None:
            if mask(l) is not True:
                continue

        if l.isdir():
            if isinstance(include_folders, str):
                if not printing.is_match(include_folders, l.name, regex):
                    continue
            elif include_folders is not None:
                try:
                    if not any(printing.is_match(n, l.name, regex)
                               for n in include_folders):
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