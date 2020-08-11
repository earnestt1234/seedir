# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 15:34:12 2020

@author: earne
"""

import os
import re

import emoji
import natsort

FILE = emoji.emojize(':page_facing_up:')
FOLDER = emoji.emojize(':file_folder:')

STYLE_DICT = {
    'lines': {'split':'├─',
              'extend':'│ ',
              'space':'  ',
              'final':'└─',
              'folderstart':'',
              'filestart':''},
    'dash':  {'split':'|-',
              'extend':'| ',
              'space':'  ',
              'final':'|-',
              'folderstart':'',
              'filestart':''},
    'spaces':{'split':'  ',
              'extend':'  ',
              'space':'  ',
              'final':'  ',
              'folderstart':'',
              'filestart':''},
    'plus':  {'split':'+-',
              'extend':'| ',
              'space':'  ',
              'final':'+-',
              'folderstart':'',
              'filestart':''},
    'arrow': {'split':'  ',
              'extend':'  ',
              'space':'  ',
              'final':'  ',
              'folderstart':'>',
              'filestart':'>'},
    'emoji': {'split':'├─',
              'extend':'│ ',
              'space':'  ',
              'final':'└─',
              'folderstart':FOLDER,
              'filestart':FILE}
    }

class SeedirError(Exception):
    """Class for representing errors from seedir"""

def count_files(paths):
    files = sum([os.path.isfile(p) for p in paths])
    return files

def count_folders(paths):
    folders = sum([os.path.isdir(p) for p in paths])
    return folders

def beyond_depth_str(beyond, paths=None):
    if beyond == 'ellipsis':
        return '...'
    elif beyond in ['contents','content']:
        folders = count_folders(paths)
        files = count_files(paths)
        return '{} folder(s), {} file(s)'.format(folders, files)
    elif beyond and beyond[0] == '_':
        return beyond[1:]
    else:
        s1 = '"beyond" must be "ellipsis", "content", or '
        s2 = 'a string starting with "_"'
        raise SeedirError(s1 + s2)

def sort_dir(root, paths, first=None, sort_reverse=False, sort_key=None):
    if first in ['folders', 'files']:
        folders = [p for p in paths if
                   os.path.isdir(os.path.join(root, p))]
        files = [p for p in paths if not
                 os.path.isdir(os.path.join(root, p))]
        folders = natsort.natsorted(folders, reverse=sort_reverse, key=sort_key)
        files = natsort.natsorted(files, reverse=sort_reverse, key=sort_key)
        return folders + files if first == 'folders' else files + folders
    else:
        return natsort.natsorted(paths, reverse=sort_reverse, key=sort_key)

def is_match(pattern, string, regex=True):
    if regex:
        return bool(re.search(pattern, string))
    else:
        return pattern == string

def recursive_folder_structure(path, depth=0, incomplete=None, split='├─',
                               extend='│ ', space='  ', final='└─',
                               filestart='', folderstart='', depthlimit=None,
                               itemlimit=None, beyond=None, first=None,
                               sort=True, sort_reverse=False, sort_key=None,
                               include=None, exclude=None, regex=True):
    output = ''
    if incomplete is None:
        incomplete = []
    if depth == 0:
        output += folderstart + os.path.basename(path) + os.sep +'\n'
    if depth == depthlimit and beyond is None:
        return output
    listdir =  os.listdir(path)
    if sort or first is not None:
        listdir = sort_dir(path, listdir, first=first,
                           sort_reverse=sort_reverse, sort_key=sort_key)
    if listdir:
        incomplete.append(depth)
    depth += 1
    if depthlimit and depth == depthlimit + 1:
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
        incomplete = [n for n in incomplete if n < depth]
        paths = [os.path.join(path, item) for item in os.listdir(path)]
        extra = beyond_depth_str(beyond, paths)
        if beyond is not None and extra:
            output += base_header + final + extra + '\n'
        return output
    items = 0
    for i, f in enumerate(listdir):
        sub = os.path.join(path, f)
        base_header = []
        max_i = max(incomplete)
        for p in range(max_i):
            if p in incomplete:
                base_header.append(extend)
            else:
                base_header.append(space)
        if i == len(os.listdir(path)) - 1:
            branch = final
            incomplete.remove(depth-1)
            incomplete = [n for n in incomplete if n < depth]
        else:
            branch = split
        base_header = ''.join(base_header)
        header = base_header + branch
        if i == itemlimit:
            paths = [os.path.join(path, rem) for rem in listdir[i:]]
            extra = beyond_depth_str(beyond, paths)
            output += base_header + final + extra + '\n'
            return output
        elif os.path.isdir(sub):
            output += header + folderstart + f + os.sep +'\n'
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
                                                 sort_reverse=sort_reverse,
                                                 sort_key=sort_key,
                                                 regex=regex)
        else:
            output += header + filestart + f + '\n'
        items += 1
    return output

def get_styleargs(style):
    if style not in STYLE_DICT:
        error_text = 'style "{}" not recognized, must be '.format(style)
        error_text += 'lines, spaces, arrow, plus, dash, or emoji'
        raise SeedirError(error_text)
    else:
        return STYLE_DICT[style]

def format_style(style_dict, indent=2):
    if indent < 0 or not isinstance(indent, int):
        raise SeedirError('indent must be a positive integer')
    elif indent == 0:
        output = {k : '' for k,_ in style_dict.items()}
    elif indent == 1:
        output = {k : v[0] for k,v in style_dict.items()}
    elif indent == 2:
        output = style_dict
    else:
        indent -= 2
        output = {k : v + v[-1]*indent for k,v in style_dict.items()}
    return output

def seedir(path, style='lines', indent=2, uniform='', depthlimit=None,
           itemlimit=None, beyond=None, first=None, sort=True,
           sort_reverse=False, sort_key=None, regex=True, **kwargs):
    if style:
        styleargs = get_styleargs(style)
    styleargs = format_style(styleargs, indent=indent)
    if uniform:
        for arg in ['extend', 'split', 'final', 'space']:
            styleargs[arg] = uniform
    for k in kwargs:
        if k in styleargs:
            styleargs[k] = styleargs[k]
    if sort_key is not None or sort_reverse == True:
        sort = True
    return recursive_folder_structure(path, depthlimit=depthlimit,
                                      itemlimit=itemlimit,
                                      beyond=beyond, first=first,
                                      sort=sort, sort_reverse=sort_reverse,
                                      sort_key=sort_key, regex=regex,
                                      **styleargs)
