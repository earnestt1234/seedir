# -*- coding: utf-8 -*-
"""
General module of resources and helpers for printing and making folder trees
in seedir.

@author: Tom Earnest

GitHub: https://github.com/earnestt1234/seedir
"""
import copy
import os
import re

import emoji

from seedir.errors import SeedirError

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
'''"Tokens" used to create folder trees in different styles'''

filepath = os.path.dirname(os.path.abspath(__file__))
wordpath = os.path.join(filepath, 'words.txt')
wordfile = open(wordpath, 'r')
words = [line.strip() for line in wordfile.readlines()]
"""List of dictionary words for seedir.randomdir()"""

# functions

def is_match(pattern, string, regex=True):
    '''Function for matching strings using either regular expression
    or literal interpretation.'''
    if regex:
        return bool(re.search(pattern, string))
    else:
        return pattern == string

def get_styleargs(style):
    '''
    Return the string tokens associated with different styles for printing
    folder trees with seedir.seedir().

    Parameters
    ----------
    style : str
        Style name.  Current options are 'lines', 'spaces', 'arrow', 'plus',
        'dash', or 'emoji'.

    Raises
    ------
    SeedirError
        Style not recognized.

    Returns
    -------
    dict
        Dictionary of tokens for the given style.

    '''
    if style not in STYLE_DICT:
        error_text = 'style "{}" not recognized, must be '.format(style)
        error_text += 'lines, spaces, arrow, plus, dash, or emoji'
        raise SeedirError(error_text)
    else:
        return copy.deepcopy(STYLE_DICT[style])

def format_indent(style_dict, indent=2):
    '''
    Format the indent of style tokens, from seedir.STYLE_DICT or returned
    by seedir.get_styleargs().

    Parameters
    ----------
    style_dict : dict
        Dictionary of style tokens.
    indent : int, optional
        Number of spaces to indent. The default is 2.  With 0, all tokens
        become the null string.  With 1, all tokens are only the first
        character.  With 2, the style tokens are returned unedited.  When >2,
        the final character of each token (except 'folderstart' and
        'filestart') are extened n - indent times, to give a string whose
        length is equal to indent.

    Raises
    ------
    SeedirError
        Indent is not a positive integer.

    Returns
    -------
    output : dict
        New dictionary of edited tokens.

    '''
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
