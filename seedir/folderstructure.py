# -*- coding: utf-8 -*-
"""
The primary algorithm for determining the folder structure returned by
`seedir.realdir.seedir()` and `seedir.fakedir.FakeDir.seedir()`.

"""

import os
import warnings

import natsort

import seedir.printing as printing

def listdir_fullpath(path):
    '''Like `os.listdir()`, but returns absolute paths.'''
    return [os.path.join(path, f) for f in os.listdir(path)]

def formatter_update_args(formatter, item, args):
    '''
    Update a dictionary of style tokens based on a formatter function and
    an item.  Added in v 0.3.0 to support the addition of the formatter parameter
    for the seedir algorithm.

    Parameters
    ----------
    formatter : function
        Formatting function.
    item : file or folder item
        String or FakeItem produced in the seedir algorithm
    styleargs : dict
        Dictionary of seedir style tokens

    Returns
    -------
    styleargs : dict
        The input dictionary, after it may have been updated.

    '''
    newstyle = formatter(item)
    if newstyle is None:
        pass
    else:
        args.update(newstyle)

    return args

class FolderStructure:
    '''General class for determining folder strctures.  Implements
    the seedir folder-tree generating algorithm over arbitrary objects.'''

    def __init__(self, getname_func, isdir_func, listdir_func):
        '''
        Defines the functions used by `self` for generating folder structures.

        Parameters
        ----------
        getname_func : function
            Returns the name of the object.
        isdir_func : function
            Returns boolean of whether child object is a folder.
        listdir_func : function
            Function for returning the children of an object, given it is a
            "folder" as determined by `isdir_func`.  The child objects returned
            should be of similar type to `self`, such that the functions can
            be recursively applied.

        Returns
        -------
        None.

        '''
        self.listdir = listdir_func
        self.isdir = isdir_func
        self.getname = getname_func

    def __call__(self, folder, style='lines', printout=True, indent=2, uniform=None,
                 anystart=None, anyend=None, depthlimit=None, itemlimit=None,
                 beyond=None, first=None, sort=False, sort_reverse=False,
                 sort_key=None, include_folders=None, exclude_folders=None,
                 include_files=None, exclude_files=None, regex=False, mask=None,
                 formatter=None, sticky_formatter=False, slash=None, **kwargs):
        '''Call this on a folder object to generate the seedir output
        for that object.'''

        accept_kwargs = ['extend', 'split', 'space', 'final',
                         'folderstart', 'filestart', 'folderend', 'fileend']

        if any(i not in accept_kwargs for i in kwargs.keys()):
            bad_kwargs = [i for i in kwargs.keys() if i not in accept_kwargs]
            raise ValueError(f'kwargs must be any of {accept_kwargs}; '
                             f'unrecognized kwargs: {bad_kwargs}')

        styleargs = printing.get_styleargs(style)
        printing.format_indent(styleargs, indent=indent)

        if uniform is not None:
            for arg in ['extend', 'split', 'final', 'space']:
                styleargs[arg] = uniform

        if anystart is not None:
            styleargs['folderstart'] = anystart
            styleargs['filestart'] = anystart

        if anyend is not None:
            styleargs['folderend'] = anyend
            styleargs['fileend'] = anyend

        if slash is not None:
            warnings.warn("`slash` will removed in a future version; "
                          "pass `folderend` as a keyword argument instead.",
                          DeprecationWarning)
            if slash.lower() in ['sep', 'os.sep']:
                slash = os.sep
            styleargs['folderend'] = slash

        for k in kwargs:
            if k in styleargs:
                styleargs[k] = kwargs[k]

        if sort_key is not None or sort_reverse == True:
            sort = True

        default_args = dict(depthlimit=depthlimit,
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
                            **styleargs)

        current_args = default_args.copy()

        # apply formatter to top level
        if formatter is not None:
            formatter_update_args(formatter, folder, current_args)

        if sticky_formatter:
            default_args = current_args

        s = self._folderstructure_recurse(folder, default_args, **current_args).strip()

        if printout:
            print(s)
        else:
            return s

    def beyond_depth_str(self, items, beyond):
        '''
        Generates the text when using the 'beyond'
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
        items : collection of file paths, optional
            Path items of the items beyond the limit, used when the 'beyond'
            argeument is 'content' or 'contents'. The default is None.


        Returns
        -------
        str
            String indicating what lies beyond

        '''
        if beyond.lower() == 'ellipsis':
            return '...'
        elif beyond.lower() in ['contents','content']:
            folders = self.count_folders(items)
            files = self.count_files(items)
            return '{} folder(s), {} file(s)'.format(folders, files)
        elif beyond and beyond[0] == '_':
            return beyond[1:]
        else:
            s1 = '"beyond" must be "ellipsis", "content", or '
            s2 = 'a string starting with "_"'
            raise ValueError(s1 + s2)

    def count_files(self, items):
        '''
        Count the number of files in a collection of paths.

        Parameters
        ----------
        paths : list-like
            Collection of paths.

        Returns
        -------
        files : int
            Count of files.

        '''
        files = sum([not self.isdir(i) for i in items])
        return files

    def count_folders(self, items):
        '''
        Count the number of folders in a collection of paths.

        Parameters
        ----------
        paths : list-like
            Collection of paths.

        Returns
        -------
        files : int
            Count of folders.

        '''
        folders = sum([self.isdir(i) for i in items])
        return folders

    def filter_items(self, listdir, include_folders=None,
                      exclude_folders=None, include_files=None,
                      exclude_files=None, regex=False, mask=None):

        '''
        Filter for folder and file names in folder structures.  Removes or includes
        items matching filtering strings.

        Note the following priority of arguments:
            1. Mask (totally overwrites include/exclude)
            2. Include (saves items from being excluded)
            3. Exclude

        Parameters
        ----------
        listdir : list-like
            Collection of file/folder items.
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

        Returns
        -------
        keep : list
            Filtered input.

        '''

        def _should_convert(x):
            return isinstance(x, str) or x is None

        filtered = []
        for item in listdir:

            name = self.getname(item)

            if self.isdir(item):
                inc = [include_folders] if _should_convert(include_folders) else include_folders
                exc = [exclude_folders] if _should_convert(exclude_folders) else exclude_folders
            else:
                inc = [include_files] if _should_convert(include_files) else include_files
                exc = [exclude_files] if _should_convert(exclude_files) else exclude_files

            # 1. check mask - which trumps include/exclude arguments
            if mask is not None:
                if mask(item):
                    filtered.append(item)
                continue

            # set default keep behavior
            # items are exluded if inclusion is passed
            keep = all([i is None for i in inc])

            # 2. apply exclusion
            for pat in exc:
                if pat is not None:
                    match = printing.is_match(pattern=pat, string=name, regex=regex)
                    if match:
                        keep = False

            # 3. apply inclusion (trumps exclusion)
            for pat in inc:
                if pat is not None:
                    match = printing.is_match(pattern=pat, string=name, regex=regex)
                    if match:
                        keep = True

            if keep:
                filtered.append(item)

        return filtered


    def _folderstructure_recurse(self, folder, default_args, depth=0, incomplete=None,
                                 extend='│ ', space='  ', split='├─', final='└─',
                                 filestart='', folderstart='', fileend='', folderend='/',
                                 depthlimit=None, itemlimit=None, beyond=None, first=None,
                                 sort=True, sort_reverse=False, sort_key=None,
                                 include_folders=None, exclude_folders=None,
                                 include_files=None, exclude_files=None,
                                 regex=False, mask=None, formatter=None, sticky_formatter=False):
        '''
        Main algorithm for creating folder structure string.  See
        `seedir.realdir.seedir()` or `seedir.fakedir.FakeDir.seedir()`
        for a description of the parameters.

        Note that since the expansion of the formatter parameter
        (version 0.3.1), the call & logic has been slightly updated.
        Primarily, the `default_args` parameter has been added, to represent
        arguments to default to when the formatter is not in use.  The actual
        keyword arguments are treated as the options to be used for `folder`,
        and can change between iterations.  The `default_args` stay the same,
        unless `sticky_formatter` is used in combination with `formatter` to
        permanently update the default arguments.

        **In almost all cases, users should not need to call this function
        to generate diagrams**.  Rather, they should use the `__call__`
        method of a `FolderStructure` instance.

        '''

        # initialize
        output = ''

        if incomplete is None:
            incomplete = []

        # root string
        if depth == 0:

            d0args = {
                'extend': extend,
                'space': space,
                'split': split,
                'final': final,
                'filestart': filestart,
                'folderstart': folderstart,
                'fileend' : fileend,
                'folderend': folderend
                }

            if formatter is not None:
                formatter_update_args(formatter, folder, d0args)
            output += (d0args['folderstart'] +
                       self.getname(folder) +
                       d0args['folderend'] +
                       '\n')


        current_itemlimit = itemlimit
        beyond_added = False

        # handle when depthlimit is reached
        if isinstance(depthlimit, int) and depth >= depthlimit:
            if beyond is None:
                return output
            else:
                current_itemlimit = 0

        # get all children, add depth to docket
        listdir = self.listdir(folder)
        incomplete.append(depth)

        # sort and filter the contents of listdir
        sortargs = {
            'first': first,
            'sort_reverse': sort_reverse,
            'sort_key': sort_key}

        filterargs = {
            'include_folders': include_folders,
            'exclude_folders': exclude_folders,
            'include_files' : include_files,
            'exclude_files': exclude_files,
            'mask': mask
            }

        if sort or first is not None:
            listdir = self.sort_dir(listdir, **sortargs)

        if any(arg is not None for arg in filterargs.values()):
            listdir = self.filter_items(listdir, **filterargs, regex=regex)

        # set current_itemlimit based on listdir size
        if current_itemlimit is None:
            current_itemlimit = len(listdir)
        else:
            current_itemlimit = min(current_itemlimit, len(listdir))

        # segment output into what can be included
        finalpaths = listdir[:current_itemlimit]
        rem = listdir[current_itemlimit:]

        # append beyond string if being used
        if beyond is not None:
            if rem or (depth == depthlimit):
                finalpaths += [self.beyond_depth_str(rem, beyond)]
                beyond_added = True

        # if empty, close the current depth
        if not finalpaths:
            incomplete.remove(depth)

        # get output for each item in folder
        for i, f in enumerate(finalpaths):

            current_args = default_args.copy() # used in this iteration
            next_default_args = default_args   # passed to child

            lastitem = (i == (len(finalpaths) - 1))
            isbeyondstr = lastitem and beyond_added
            name = f if isbeyondstr else self.getname(f)

            # update tokens with formatter if passed
            if not isbeyondstr and formatter is not None:
                formatter_update_args(formatter, f, current_args)

            if sticky_formatter:
                next_default_args = current_args

            # create header for the item
            base_header = self.get_base_header(incomplete,
                                               current_args['extend'],
                                               current_args['space'])

            if lastitem:
                branch = current_args['final']
                incomplete.remove(depth)
            else:
                branch = current_args['split']

            header = base_header + branch

            # concat to output and recurse if item is folder
            if not isbeyondstr and self.isdir(f):
                output += (header +
                           current_args['folderstart'] +
                           name +
                           current_args['folderend'] +
                           '\n')
                output += self._folderstructure_recurse(f, depth=depth + 1,
                                                        incomplete=incomplete,
                                                        default_args=next_default_args,
                                                        **current_args)

            # only concat to output if file
            else:
                output += (header +
                           current_args['filestart'] +
                           name +
                           current_args['fileend'] +
                           '\n')

        return output

    def get_base_header(self, incomplete, extend, space):
        '''
        For folder structures, generate the combination of extend and space
        tokens to prepend to file names when generating folder diagrams.


        The string generated here will still be missing the branch token
        (split or final) as well as any folderstart or filestart tokens.
        They are added within seedir.seedir().

        For any item included in a folder diagram, the combination of
        extend and space tokens is based on the depth of the item as well as the
        parent folders to that item which are not completed.  This information
        is symbolized with the `incomplete` argument.  The following illustrates
        the incomplete arguments passed to this function for an example folder
        tree:

        ```
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
        ```

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

    def sort_dir(self, items, first=None, sort_reverse=False, sort_key=None):
        '''
        Sorting function used to sort contents when producing folder diagrams.

        Parameters
        ----------
        items : list-like
            Collection of folder contents.
        first : 'files' or 'folders', optional
            Sort either files or folders first. The default is None.
        sort_reverse : bool, optional
            Reverse the sort applied. The default is False.
        sort_key : function, optional
            Function to apply to sort the objs by their basename.  The function
            should take a single argument, of the type expected by
            this FolderStucture.

        Returns
        -------
        list
            Sorted input as a list.

        '''
        if sort_key is None:
            key = lambda x : self.getname(x)
        else:
            key = lambda x: sort_key(self.getname(x))

        if first in ['folders', 'files']:
            folders = [p for p in items if self.isdir(p)]
            files = [p for p in items if not self.isdir(p)]
            folders = natsort.natsorted(folders, reverse=sort_reverse, key=key)
            files = natsort.natsorted(files, reverse=sort_reverse, key=key)
            output = folders + files if first == 'folders' else files + folders
        elif first is None:
            output = list(natsort.natsorted(items, reverse=sort_reverse, key=key))
        else:
            raise ValueError("`first` must be 'folders', 'files', or None.")

        return output

slashes = os.sep + '/' + '//'

RealDirStructure = FolderStructure(getname_func = lambda x: os.path.basename(x.rstrip(slashes)),
                                   isdir_func = lambda x: os.path.isdir(x),
                                   listdir_func = listdir_fullpath)
"""Object for making real folder structures from string paths."""

PathlibStructure = FolderStructure(getname_func = lambda x: x.name,
                                   isdir_func = lambda x: x.is_dir(),
                                   listdir_func = lambda x: list(x.iterdir()))
"""Object for making real folder structures from pathlib objects."""

FakeDirStructure = FolderStructure(getname_func = lambda x: x.name,
                                   isdir_func = lambda x: x.isdir(),
                                   listdir_func = lambda x: x.listdir())
"""Object for making fake folder structures."""
