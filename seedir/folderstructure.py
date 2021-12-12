# -*- coding: utf-8 -*-
"""
The primary algorithm for determining the folder structure returned by
`seedir.realdir.seedir()` and `seedir.fakedir.FakeDir.seedir()`.

"""

import os

from seedir.folderstructurehelpers import (listdir_fullpath,
                                           sort_dir,
                                           sort_fakedir,
                                           filter_item_names,
                                           filter_fakeitem_names,
                                           beyond_depth_str,
                                           beyond_fakedepth_str,
                                           get_base_header,
                                           formatter_update_styleargs)

class FolderStructure:
    '''General class for determining folder strctures.'''
    def __init__(self, listdir_func, sort_func, filter_func, isdir_func,
                 getname_func, beyondstr_func):
        '''
        Defines the functions used by `self` for generating folder structures.

        Parameters
        ----------
        listdir_func : function
            Function for returning the children of an object, given it is a
            "folder" as determined by `isdir_func`.  The child objects returned
            should be of similar type to `self`, such that the functions can
            be recursively applied.
        sort_func : function
            Function for sorting the output of `listdir_func`.  Should handle
            the `first`, `sort_key`, and `sort_reverse` parameters.
        filter_func : function
            Function for filtering the output of `listdir_func`.  Should handle
            the include/exclude folder/file paramters, as well as `mask`.
        isdir_func : function
            Returns boolean of whether child object is a folder.
        getname_func : function
            Returns the name of the object.
        beyondstr_func : function
            Determines the "beyond" string based on a list of objects.
            See `seedir.folderstructurehelpers.py` for example.

        Returns
        -------
        None.

        '''
        self.listdir = listdir_func
        self.sort = sort_func
        self.filter = filter_func
        self.isdir = isdir_func
        self.getname = getname_func
        self.beyondstr = beyondstr_func

    def _folderstructure(self, folder, depth=0, incomplete=None, extend='│ ',
                         space='  ', split='├─', final='└─',
                         filestart='', folderstart='', depthlimit=None,
                         itemlimit=None, beyond=None, first=None,
                         sort=True, sort_reverse=False, sort_key=None,
                         include_folders=None, exclude_folders=None,
                         include_files=None, exclude_files=None,
                         regex=False, mask=None, formatter=None, slash='/'):
        '''
        Main algorithm for creating folder structure string.  See
        `seedir.realdir.seedir()` or `seedir.fakedir.FakeDir.seedir()`
        for a description of the parameters.

        '''

        # collect style arguments
        styleargs = {
            'extend': extend,
            'space': space,
            'split': split,
            'final': final,
            'filestart': filestart,
            'folderstart': folderstart
            }

        # initialize
        output = ''

        if incomplete is None:
            incomplete = []

        if depth == 0:
            if formatter is not None:
                formatter_update_styleargs(formatter, folder, styleargs)
            output += (styleargs['folderstart'] +
                       self.getname(folder) +
                       slash +
                       '\n')

        current_itemlimit = itemlimit
        beyond_added = False

        # handle when depthlimit is reached
        if depth == depthlimit:
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
            listdir = self.sort(listdir, **sortargs)

        if any(arg is not None for arg in filterargs.values()):
            listdir = self.filter(listdir, **filterargs, regex=regex,)

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
                finalpaths += [self.beyondstr(rem, beyond)]
                beyond_added = True

        # if empty, close the current depth
        if not finalpaths:
            incomplete.remove(depth)

        # get output for each item in folder
        for i, f in enumerate(finalpaths):

            lastitem = (i == (len(finalpaths) - 1))
            isbeyondstr = lastitem and beyond_added
            name = f if isbeyondstr else self.getname(f)

            # update tokens with formatter if passed
            if formatter is not None:
                formatter_update_styleargs(formatter, f, styleargs)

            # create header for the item
            base_header = get_base_header(incomplete,
                                          styleargs['extend'],
                                          styleargs['space'])

            if lastitem:
                branch = styleargs['final']
                incomplete.remove(depth)
            else:
                branch = styleargs['split']

            header = base_header + branch

            # concat to output and recurse if item is folder
            if not isbeyondstr and self.isdir(f):
                output += header + styleargs['folderstart'] + name + slash +'\n'
                output += self._folderstructure(f, depth=depth + 1,
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
                                                formatter=formatter,
                                                slash=slash)

            # only concat to output if file
            else:
                output += header + styleargs['filestart'] + name + '\n'

        return output

    def __call__(self, folder, **kwargs):
        return self._folderstructure(folder, **kwargs).strip()

slashes = os.sep + '/' + '//'

realdir_params = dict(listdir_func = listdir_fullpath,
                      sort_func = sort_dir,
                      filter_func = filter_item_names,
                      isdir_func = lambda x: os.path.isdir(x),
                      getname_func = lambda x: os.path.basename(x.rstrip(slashes)),
                      beyondstr_func = beyond_depth_str)

fakedir_params = dict(listdir_func = lambda x: x.listdir(),
                      sort_func = sort_fakedir,
                      filter_func = filter_fakeitem_names,
                      isdir_func = lambda x: x.isdir(),
                      getname_func = lambda x: x.name,
                      beyondstr_func = beyond_fakedepth_str)

RealDirStructure = FolderStructure(**realdir_params)
"""Object for making real folder structures."""

FakeDirStructure = FolderStructure(**fakedir_params)
"""Object for making fake folder structures."""