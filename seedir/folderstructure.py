# -*- coding: utf-8 -*-
"""
The primary algorithm for determining the folder structure returned by
`seedir.realdir.seedir()` and `seedir.fakedir.FakeDir.seedir()`.

"""

from abc import ABC, abstractmethod
import copy
import math
import os

import natsort

import seedir.printing as printing

def listdir_fullpath(path):
    '''Like `os.listdir()`, but returns absolute paths.'''
    return [os.path.join(path, f) for f in os.listdir(path)]

class FolderStructureArgs:

    def __init__(self, extend='│ ', space='  ', split='├─', final='└─',
                 filestart='', folderstart='', fileend='', folderend='/',
                 depthlimit=None, itemlimit=None, beyond=None, first=None,
                 sort=True, sort_reverse=False, sort_key=None,
                 include_folders=None, exclude_folders=None,
                 include_files=None, exclude_files=None,
                 regex=False, mask=None, formatter=None,
                 sticky_formatter=False, acceptable_listdir_errors=None,
                 denied_string=' [ACCESS DENIED]'):
        self.extend = extend
        self.space = space
        self.split = split
        self.final = final
        self.filestart = filestart
        self.folderstart = folderstart
        self.fileend = fileend
        self.folderend = folderend
        self.depthlimit = depthlimit
        self.itemlimit = itemlimit
        self.beyond = beyond
        self.first = first
        self.sort = sort
        self.sort_reverse = sort_reverse
        self.sort_key = sort_key
        self.include_folders = include_folders
        self.exclude_folders = exclude_folders
        self.include_files = include_files
        self.exclude_files = exclude_files
        self.regex = regex
        self.mask = mask
        self.formatter = formatter
        self.sticky_formatter = sticky_formatter
        self.acceptable_listdir_errors = acceptable_listdir_errors
        self.denied_string = denied_string

    def copy(self):
        return copy.deepcopy(self)

    def update_with_formatter(self, formatter, item):
        newstyle = formatter(item)
        if newstyle is None:
            return
        for k, v in newstyle.items():
            setattr(self, k, v)

class FolderStructure(ABC):
    '''General class for determining folder strctures.  Implements
    the seedir folder-tree generating algorithm over arbitrary objects.

    **This is an abstract class that cannot be instantiated directly.**  It must
    be subclassed, and the user must imeplement three abstract methods:

        - `getname(self, item)`: Return the string name of a folder or file object.
        - `isdir(self, item)`: Return a boolean indicating whether an object is
        a folder (i.e., can be further travesed) or not.
        - `listdir(self, item)`: For a folder-like object, return its children,
        such that these same three methods can be called on each child again
        (recursively).

    Details on each of these functions are provided below.  In each case,
    `item` is a folder-like or file-like object that can be listed in the
    diagram.

    Seedir provides implementations for string paths (`RealDirStructure`),
    pathlib objects (`PathibStucture`), and "fakedir" objects (`FakeDirStucture`).

    *Note: Prior to v0.5.0, you could initialize a FolderStructure by passing
    these three functions as arguments to the constructor.  This is now
    deprecated and will throw an error.*
    '''

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # ABSTRACT METHODS WHICH REQUIRE IMPLEMENTATION
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @abstractmethod
    def getname(self, item):
        '''
        Generate a string name for an item to put in the tree diagram.

        Parameters
        ----------
        item : user-specified
            Folder-like or file-like object.

        Returns
        -------
        name : str
            Name to show in the diagram.

        '''
        ...

    @abstractmethod
    def isdir(self, item):
        '''
        Returns True if an object is folder-like.

        This function determines whether to treat objects as a folder or a
        file.  Some key differences of note are:

        - Folders **will** be passed to `listdir()` to retrieve their
        children.  Files are instead not passed to this function.
        - Some arguments are unique to folders or files, e.g.
        `exclude_folders` and `exclude_files`.
        - Folders and files are (by default) represented differently
        in diagrams, with folders usually ending with a slash.

        Parameters
        ----------
        item : user-specified
            Folder-like or file-like object.

        Returns
        -------
        result : bool
            True if item is folder; False if not.

        '''
        ...

    @abstractmethod
    def listdir(self, item):
        '''
        Return the children of a folder-type object.

        Children should always be more objects which can be passed to
        `getname()`, `isdir()`, or (in the case of folder-like objects)
        `listdir()`.

        This function is not called on objects which are not folders,
        as determined by `isdir()`.

        Parameters
        ----------
        item : user-specified
            Folder-like or file-like object.

        Returns
        -------
        children : list
            List of child objects for further traversal.  Can be empty
            for a folder with no children.

        '''
        ...

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __call__(self, folder, style='lines', printout=True, indent=2, uniform=None,
                 anystart=None, anyend=None, depthlimit=None, itemlimit=None,
                 beyond=None, first=None, sort=False, sort_reverse=False,
                 sort_key=None, include_folders=None, exclude_folders=None,
                 include_files=None, exclude_files=None, regex=False, mask=None,
                 formatter=None, sticky_formatter=False,
                 acceptable_listdir_errors=None, denied_string='', **kwargs):
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

        for k in kwargs:
            if k in styleargs:
                styleargs[k] = kwargs[k]

        if sort_key is not None or sort_reverse == True:
            sort = True

        if acceptable_listdir_errors is None:
            acceptable_listdir_errors = tuple()

        args = FolderStructureArgs(depthlimit=depthlimit,
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
                                   **styleargs)


        s = self._folder_structure_recurse(ITEM=folder,
                                           FSARGS=args).strip()

        if printout:
            print(s)
        else:
            return s

    def apply_itemlimit(self, items, itemlimit):
        '''
        Limit the number of children in a folder.

        Parameters
        ----------
        items : list
            Child items.
        itemlimit : int, tuple, or None
            Limit.  If int, limits the number of items regardless of if they
            are folders or file.  If a 2-tuple, the first number is treated
            as a limit on the number of folders and the second number
            is treated as a limit on the number of files.  If None,
            no limit is applied.

        Returns
        -------
        finalitems : list
            Kept times.
        rem : list
            Omitted items.

        '''

        # all items included when None
        if itemlimit is None:
            itemlimit = len(items)

        # if int, take the first itemlimit items
        if isinstance(itemlimit, int):
            itemlimit = min(itemlimit, len(items))
            finalitems = items[:itemlimit]
            rem = items[itemlimit:]

        # if tuple, interpret as limits for folders and files
        else:
            finalitems, rem = self._apply_tuple_itemlimit(items, itemlimit)

        return finalitems, rem

    def _apply_tuple_itemlimit(self, items, itemlimit):
        '''Apply the itemlimit when it is a 2-tuple of
        (folderlimit, filelimit).'''
        folderlimit, filelimit = itemlimit

        folderlimit = math.inf if folderlimit is None else folderlimit
        filelimit = math.inf if filelimit is None else filelimit

        finalitems = []
        rem = []
        foldercount = 0
        filecount = 0

        for item in items:
            isdir = self.isdir(item)

            if isdir and (foldercount < folderlimit):
                finalitems.append(item)
                foldercount += 1
            elif isdir:
                rem.append(item)
            elif not isdir and (filecount < filelimit):
                finalitems.append(item)
                filecount += 1
            else:
                rem.append(item)

        return finalitems, rem

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

    def _folder_structure_recurse(self, ITEM, FSARGS, DEPTH=0,
                                  INDEX=0, INCOMPLETE=None,
                                  IS_LASTITEM=False,
                                  IS_RAWSTRING=False):

        # initialization
        OUTPUT = ''

        if INCOMPLETE is None:
            INCOMPLETE = []

        # set some variables
        is_rootitem = DEPTH == 0
        is_lastitem = IS_LASTITEM
        is_rawstring = IS_RAWSTRING

        # APPLY FORMATTER
        # # # # # # # # # # # # # #
        args = FSARGS.copy()
        next_args = FSARGS

        if not is_rawstring and args.formatter is not None:
            args.update_with_formatter(args.formatter, ITEM)

        if args.sticky_formatter:
            next_args = args

        # GET CHILDREN
        # # # # # # # # # # # # # #

        error_listing = False

        if not is_rawstring and self.isdir(ITEM):
            try:
                listdir = self.listdir(ITEM)
            except args.acceptable_listdir_errors:
                error_listing = True
                listdir = None
        else:
            listdir = None

        # ADD CURRENT ITEM TO OUTPUT
        # # # # # # # # # # # # # #

        # create header
        base_header = self.get_base_header(INCOMPLETE,
                                           args.extend,
                                           args.space)

        # handle ultimate token in header
        if is_rootitem:
            branch = ''
        elif is_lastitem:
            branch = args.final
        else:
            branch = args.split

        header = base_header + branch

        # start / end tokens
        if is_rawstring:
            fkey = 'file'
        else:
            fkey = 'folder' if self.isdir(ITEM) else 'file'

        start = f'{fkey}start'
        end = f'{fkey}end'

        # add current item to string
        name = self.getname(ITEM) if not is_rawstring else ITEM
        error_tag = args.denied_string if error_listing else ''

        OUTPUT += (header +
                   getattr(args, start) +
                   name +
                   getattr(args, end) +
                   error_tag +
                   '\n')

        if is_lastitem and INCOMPLETE:
            INCOMPLETE.remove(DEPTH-1)

        # EXIT IF NOT FOLDER
        # # # # # # # # # # # # # #

        if listdir is None:
            return OUTPUT

        # FILTER/SORT CHILDREN
        # # # # # # # # # # # # #

        current_itemlimit = args.itemlimit

        # handle when depthlimit is reached
        if isinstance(args.depthlimit, int) and DEPTH >= args.depthlimit:
            if args.beyond is None:
                return OUTPUT
            else:
                current_itemlimit = 0

        # sort and filter the contents of listdir
        sortargs = {
            'first': args.first,
            'sort_reverse': args.sort_reverse,
            'sort_key': args.sort_key}

        filterargs = {
            'include_folders': args.include_folders,
            'exclude_folders': args.exclude_folders,
            'include_files' : args.include_files,
            'exclude_files': args.exclude_files,
            'mask': args.mask,
            }

        if args.sort or args.first is not None:
            listdir = self.sort_dir(listdir, **sortargs)

        if any(arg is not None for arg in filterargs.values()):
            listdir = self.filter_items(listdir, **filterargs, regex=args.regex)

        # apply itemlimit
        finalitems, rem = self.apply_itemlimit(listdir, current_itemlimit)

        # append beyond string if being used
        beyond_added = False
        if args.beyond is not None:
            if rem or (DEPTH == args.depthlimit):
                finalitems += [self.beyond_depth_str(rem, args.beyond)]
                beyond_added = True

        # RECURSE
        # # # # # # # # # # # # # #

        if finalitems:
            INCOMPLETE.append(DEPTH)

        total = len(finalitems)

        for i, x in enumerate(finalitems):
            last = i == (total - 1)
            IS_RAWSTRING = (beyond_added and last)
            OUTPUT += self._folder_structure_recurse(x, DEPTH=DEPTH+1,
                                                     INCOMPLETE=INCOMPLETE,
                                                     FSARGS=next_args,
                                                     INDEX=i,
                                                     IS_LASTITEM=last,
                                                     IS_RAWSTRING=IS_RAWSTRING)


        # RETURN
        # # # # # # # # # # # # # #
        return OUTPUT

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
        if not incomplete:
            return ''

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

class RealDirStructure(FolderStructure):
    """Make folder structures from string paths."""

    def __init__(self):
        super().__init__()
        self.slashes = os.sep + '/' + '//'

    def getname(self, item):
        return os.path.basename(item.rstrip(self.slashes))

    def isdir(self, item):
        return os.path.isdir(item)

    def listdir(self, item):
        return listdir_fullpath(item)

class PathlibStructure(FolderStructure):
    """Make folder structures from pathlib objects."""

    def getname(self, item):
        return item.name

    def isdir(self, item):
        return item.is_dir()

    def listdir(self, item):
        return list(item.iterdir())

class FakeDirStructure(FolderStructure):
    """Make `seedir.fakedir.FakeDir` folder structures."""

    def getname(self, item):
        return item.name

    def isdir(self, item):
        return item.isdir()

    def listdir(self, item):
        return item.listdir()
