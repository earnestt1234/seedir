# -*- coding: utf-8 -*-
"""
Created on Wed May 19 10:23:38 2021

@author: earne
"""

import os

from seedir.folderstructurehelpers import (listdir_fullpath,
                                           sort_dir,
                                           sort_fakedir,
                                           filter_item_names,
                                           filter_fakeitem_names,
                                           beyond_depth_str,
                                           beyond_fakedepth_str,
                                           get_base_header)

class FolderStructure:
    def __init__(self, listdir_func, sort_func, filter_func, isdir_func,
                 getname_func, beyondstr_func):
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
                         regex=False, mask=None, slash='/'):

        # initialize
        output = ''
        if incomplete is None:
            incomplete = []
        if depth == 0:
            output += (folderstart +
                       self.getname(folder).rstrip(os.sep) +
                       slash +
                       '\n')
        current_itemlimit = itemlimit
        beyond_added = False

        # stop when too deep
        if depth == depthlimit:
            if beyond is None:
                return output
            else:
                current_itemlimit = 0

        fulllistdir = self.listdir(folder)
        incomplete.append(depth)

        # sort and trim the contents of listdir
        if sort or first is not None:
            listdir = self.sort(fulllistdir, first=first,
                                sort_reverse=sort_reverse, sort_key=sort_key)

        filterargs = {
            'include_folders': include_folders,
            'exclude_folders': exclude_folders,
            'include_files' : include_files,
            'exclude_files': exclude_files,
            'mask': mask
            }

        if any(arg is not None for arg in filterargs.values()):
            listdir = self.filter(listdir, **filterargs, regex=regex,)

        # set current_itemlimit based on listdir size
        if current_itemlimit is None:
            current_itemlimit = len(listdir)
        else:
            current_itemlimit = min(current_itemlimit, len(listdir))

        finalpaths = listdir[:current_itemlimit]
        rem = listdir[current_itemlimit:]
        if beyond is not None:
            if rem or (depth == depthlimit):
                finalpaths += [self.beyondstr(rem, beyond)]
                beyond_added = True

        if not finalpaths:
            incomplete.remove(depth)

        # get output for each item in folder
        for i, f in enumerate(finalpaths):
            lastitem = (i == (len(finalpaths) - 1))
            isbeyondstr = lastitem and beyond_added
            name = f if isbeyondstr else self.getname(f)

            # create header for the item
            base_header = get_base_header(incomplete, extend, space)
            if lastitem:
                branch = final
                incomplete.remove(depth)
            else:
                branch = split
            header = base_header + branch

            # concat to output and recurse if item is folder
            if not isbeyondstr and self.isdir(f):
                output += header + folderstart + name + slash +'\n'
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
                                                     slash=slash)

            # only concat to output if file
            else:
                output += header + filestart + name + '\n'
        return output

    def __call__(self, folder, **kwargs):
        return self._folderstructure(folder, **kwargs).strip()

realdir_params = dict(listdir_func = listdir_fullpath,
                      sort_func = sort_dir,
                      filter_func = filter_item_names,
                      isdir_func = lambda x: os.path.isdir(x),
                      getname_func = lambda x: os.path.basename(x),
                      beyondstr_func = beyond_depth_str)

fakedir_params = dict(listdir_func = lambda x: x.listdir(),
                      sort_func = sort_fakedir,
                      filter_func = filter_fakeitem_names,
                      isdir_func = lambda x: x.isdir(),
                      getname_func = lambda x: x.name,
                      beyondstr_func = beyond_fakedepth_str)

RealDirStructure = FolderStructure(**realdir_params)
FakeDirStructure = FolderStructure(**fakedir_params)