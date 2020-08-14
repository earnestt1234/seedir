# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 15:01:15 2020

@author: earne
"""
import emoji
import re

from errors import SeedirError

FILE = emoji.emojize(':page_facing_up:' + ' ')
FOLDER = emoji.emojize(':file_folder:' + ' ')

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

wordfile = open('words.txt', 'r')
words = [line.strip() for line in wordfile.readlines()]

def is_match(pattern, string, regex=True):
    if regex:
        return bool(re.search(pattern, string))
    else:
        return pattern == string

def get_styleargs(style):
    if style not in STYLE_DICT:
        error_text = 'style "{}" not recognized, must be '.format(style)
        error_text += 'lines, spaces, arrow, plus, dash, or emoji'
        raise SeedirError(error_text)
    else:
        return STYLE_DICT[style]

def format_indent(style_dict, indent=2):
    folder = style_dict['folderstart']
    file = style_dict['filestart']
    if indent < 0 or not isinstance(indent, int):
        raise SeedirError('indent must be a positive integer')
    elif indent == 0:
        output = {k : '' for k,_ in style_dict.items()
                  if k not in ['folderstart','filestart']}
    elif indent == 1:
        output = {k : v[0] for k,v in style_dict.items()
                  if k not in ['folderstart','filestart']}
    elif indent == 2:
        output = style_dict
    else:
        indent -= 2
        output = {k : v + v[-1]*indent for k,v in style_dict.items()
                  if k not in ['folderstart','filestart']}
    output['folderstart'] = folder
    output['filestart'] = file
    return output

