# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 15:34:12 2020

@author: earne
"""

import os

STYLE_DICT = {'lines':{'split':'├───',
                       'dline':'│   ',
                       'space':'    ',
                       'final':'└───'},
              'spaces':{'split':'    ',
                        'dline':'    ',
                        'space':'    ',
                        'final':'    '}}

def recursive_print(path, level=0, incomplete=[], split='├───', dline='│   ', space='    ', final='└───'):
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
        raise Exception
    else:
        return STYLE_DICT[style]

def seedir(path, style='lines'):
    styleargs = {}
    if style:
        styleargs = get_style(style)
    return recursive_print(path, **styleargs)