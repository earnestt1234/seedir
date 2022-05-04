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
                                           formatter_update_args)

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

    def _folderstructure(self, folder, default_args, depth=0, incomplete=None, extend='│ ',
                         space='  ', split='├─', final='└─',
                         filestart='', folderstart='', depthlimit=None,
                         itemlimit=None, beyond=None, first=None,
                         sort=True, sort_reverse=False, sort_key=None,
                         include_folders=None, exclude_folders=None,
                         include_files=None, exclude_files=None,
                         regex=False, mask=None, formatter=None, sticky_formatter=False,
                         slash='/'):
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

        '''

        # initialize
        output = ''

        if incomplete is None:
            incomplete = []

        if depth == 0:

            d0args = {
                'extend': extend,
                'space': space,
                'split': split,
                'final': final,
                'filestart': filestart,
                'folderstart': folderstart,
                'slash': slash
                }

            if formatter is not None:
                formatter_update_args(formatter, folder, d0args)
            output += (d0args['folderstart'] +
                       self.getname(folder) +
                       d0args['slash'] +
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
            base_header = get_base_header(incomplete,
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
                           current_args['slash'] +
                           '\n')
                output += self._folderstructure(f, depth=depth + 1,
                                                incomplete=incomplete,
                                                default_args=next_default_args,
                                                **current_args)

            # only concat to output if file
            else:
                output += (header +
                           current_args['filestart'] +
                           name +
                           '\n')

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