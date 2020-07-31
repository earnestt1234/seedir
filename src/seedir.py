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
              'spaces':{'split':'  ',
                        'dline':'  ',
                        'space':'  ',
                        'final':'  '}}

class SeedirError(Exception):
    """Class for representing errors from seedir"""

def recursive_print(path, level=0, incomplete=[], split='├─', dline='│ ',
                    space='  ', final='└─'):
    output = ''
    last = False
    if level == 0:
        output += os.path.basename(path) + '/\n'
    level += 1
    incomplete.append(level-1)
    for i, f in enumerate(os.listdir(path)):
        sub = os.path.join(path, f)
        if i == len(os.listdir(path)) - 1:
            branch = final
            last = True
        else:
            branch = split
        lines = len([i for i in incomplete if i < level-1])
        spaces = level - lines -1
        spaces = spaces if spaces > 0 else 0
        header = dline*lines + space*spaces + branch
        if last:
            incomplete.remove(level-1)
        if os.path.isdir(sub):
            output += header + f + '/\n'
            output += recursive_print(sub, level=level, incomplete=incomplete,
                                      split=split, dline=dline, space=space,
                                      final=final)
        else:
            output += header + f + '\n'
    return output

def get_style(style):
    if style not in STYLE_DICT:
        error_text = 'style "{}" not recognized, must be '.format(style)
        error_text += 'lines, spaces, or emoji'
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

def seedir(path, style='lines', indent=2):
    styleargs = {}
    if style:
        styleargs = get_style(style)
    styleargs = format_style(styleargs, indent=indent)
    return recursive_print(path, **styleargs)