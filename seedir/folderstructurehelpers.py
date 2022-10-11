# -*- coding: utf-8 -*-
"""
Helpers for creating folder structures, used by `seedir.folderstructure`.

"""
import os

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
