# -*- coding: utf-8 -*-
"""
General module of resources and helpers for printing and making folder trees
in seedir.

"""
__pdoc__ = {}

for key in ['is_match',
            'format_indent',
            'words']:
    __pdoc__[key] = False

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
              'filestart':'',
              'folderend': '/',
              'fileend': ''},
    'dash':  {'split':'|-',
              'extend':'| ',
              'space':'  ',
              'final':'|-',
              'folderstart':'',
              'filestart':'',
              'folderend': '/',
              'fileend': ''},
    'spaces':{'split':'  ',
              'extend':'  ',
              'space':'  ',
              'final':'  ',
              'folderstart':'',
              'filestart':'',
              'folderend': '/',
              'fileend': ''},
    'plus':  {'split':'+-',
              'extend':'| ',
              'space':'  ',
              'final':'+-',
              'folderstart':'',
              'filestart':'',
              'folderend': '/',
              'fileend': ''},
    'arrow': {'split':'  ',
              'extend':'  ',
              'space':'  ',
              'final':'  ',
              'folderstart':'>',
              'filestart':'>',
              'folderend': '/',
              'fileend': ''},
    'emoji': {'split':'├─',
              'extend':'│ ',
              'space':'  ',
              'final':'└─',
              'folderstart':FOLDER,
              'filestart':FILE,
              'folderend': '/',
              'fileend': ''}
    }
'''"Tokens" used to create folder trees in different styles'''

filepath = os.path.dirname(os.path.abspath(__file__))
wordpath = os.path.join(filepath, 'words.txt')
with open(wordpath, 'r') as wordfile:
    words = [line.strip() for line in wordfile.readlines()]
"""List of dictionary words for seedir.fakedir.randomdir()"""

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
    folder trees with `seedir.realdir.seedir()`.

    Parameters
    ----------
    style : str
        Style name.  Current options are `'lines'`, `'spaces'`, `'arrow'`,
        `'plus'`, `'dash'`, or `'emoji'`.

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

    Note that as of v0.3.1, the dictionary is modified in place,
    rather than a new copy being created.

    Parameters
    ----------
    style_dict : dict
        Dictionary of style tokens.
    indent : int, optional
        Number of spaces to indent. The default is 2.  With 0, all tokens
        become the null string.  With 1, all tokens are only the first
        character.  With 2, the style tokens are returned unedited.  When >2,
        the final character of each token (excep the file/folder start/end tokens)
        are extened n - indent times, to give a string whose
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
    indentable = ['split', 'extend', 'space', 'final']
    if indent < 0 or not isinstance(indent, int):
        raise SeedirError('indent must be a non-negative integer')
    elif indent == 0:
        for key in indentable:
            style_dict[key] = ''
    elif indent == 1:
        for key in indentable:
            style_dict[key] = style_dict[key][0]
    elif indent > 2:
        extension = indent - 2
        for key in indentable:
            val = style_dict[key]
            style_dict[key] = val + val[-1] * extension

    return None
