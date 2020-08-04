# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 15:34:12 2020

@author: earne
"""

import os

import emoji

STYLE_DICT = {'lines':{'split':'├─',
                       'dline':'│ ',
                       'space':'  ',
                       'final':'└─'},
              'dash':{'split':'|-',
                      'dline':'| ',
                      'space':'  ',
                      'final':'|-'},
              'spaces':{'split':'  ',
                        'dline':'  ',
                        'space':'  ',
                        'final':'  '},
              'plus':{'split':'+-',
                       'dline':'| ',
                       'space':'  ',
                       'final':'+-'}}

class SeedirError(Exception):
    """Class for representing errors from seedir"""

def get_folder_structure(path, level=0, incomplete=None, split='├─', dline='│ ',
                         space='  ', final='└─', filestart='', folderstart='',
                         levellimit=None, levellimitstyle=None):
    output = ''
    if incomplete is None:
        incomplete = []
    if level == 0:
        output += folderstart + os.path.basename(path) + os.sep +'\n'
    if level == levellimit and levellimitstyle == None:
        return output
    level += 1
    incomplete.append(level-1)
    for i, f in enumerate(os.listdir(path)):
        sub = os.path.join(path, f)
        header = []
        max_i = max(incomplete)
        for p in range(max_i):
            if p in incomplete:
                header.append(dline)
            else:
                header.append(space)
        if i == len(os.listdir(path)) - 1:
            branch = final
            incomplete.remove(level-1)
            incomplete = [i for i in incomplete if i < level]
        else:
            branch = split
        header = ''.join(header) + branch
        if level == levellimit:
            output += header + '. . .\n'
            return output
        elif os.path.isdir(sub):
            output += header + folderstart + f + os.sep +'\n'
            output += get_folder_structure(sub, level=level, incomplete=incomplete,
                                           split=split, dline=dline, space=space,
                                           final=final, filestart=filestart,
                                           folderstart=folderstart,
                                           levellimit=levellimit)
        else:
            output += header + filestart + f + '\n'
    return output

def get_style(style):
    if style == 'arrow':
        style = 'spaces'
    if style == 'emoji':
        style = 'lines'
    if style not in STYLE_DICT:
        error_text = 'style "{}" not recognized, must be '.format(style)
        error_text += 'lines, spaces, arrow, plus, dash, or emoji'
        raise SeedirError(error_text)
    else:
        return STYLE_DICT[style]

def get_file_folder_start(style):
    d = {'filestart' : '',
         'folderstart' : ''}
    if style == 'arrow':
        d['filestart'] = '>'
        d['folderstart'] = '>'
    if style == 'emoji':
        d['filestart'] = emoji.emojize(':page_facing_up:')
        d['folderstart'] = emoji.emojize(':file_folder:')
    return d

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

def seedir(path, style='lines', indent=2, uniform='', levellimit=None,
           **kwargs):
    styleargs = {}
    startargs = {}
    if style:
        styleargs = get_style(style)
        startargs = get_file_folder_start(style)
    styleargs = format_style(styleargs, indent=indent)
    allargs = {**styleargs, **startargs}
    if uniform:
        for arg in ['dline', 'split', 'final', 'space']:
            allargs[arg] = uniform
    for k in kwargs:
        if k in allargs:
            allargs[k] = kwargs[k]
    return get_folder_structure(path, levellimit=levellimit, **allargs)
