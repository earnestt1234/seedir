#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 22:21:12 2020

@author: earnestt1234
"""

import getopt, os, sys

import seedir as sd

help_letters = 'hp:y:d:i:b:s:r:'

long_opts = ['path=', 'style=', 'depthlimit=', 'itemlimit=',
             'beyond=', 'sort=', 'sort_reverse=']

help_str = '''Help for command seedir.  Function for printing a folder tree
structure.

Basically calls seedir.seedir() (with some options removed).

Options:

-p --path= <DEFAULT : os.getcwd()>
    System path (in quotes)

-y --style= <DEFAULT : 'lines'>
    Style for the folder diagram.  Options are "lines", "spaces", "dash",
    "arrow", "plus", or "emoji".

-d --depthlimit= <DEFAULT : 3>
    Limit on depth of folders to enter.

-i --itemlimit= <DEFAULT : 10>
    Limit on the number of items to include per directory.

-b --beyond= <DEFAULT : 'content'>
    Way to represent items past the depthlimit or itemlimit.  Options are
    'content' or 'ellipsis'.

-s --sort <DEFAULT : False>
    Sort the contents of each directory (by name).

-r --sort_reverse <DEFAULT : False>
    Reverse the sort.
'''

def main(argv=None):
    if argv is  None:
        argv = sys.argv[1:]
    path = os.getcwd()
    style = 'lines'
    depthlimit = 3
    itemlimit = 10
    beyond = 'content'
    sort = False
    sort_reverse = False
    try:
       opts, args = getopt.getopt(argv, help_letters, long_opts)
    except getopt.GetoptError:
       print(help_str)
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
           print(help_str)
           sys.exit()
       elif opt in ("-p", "--path"):
           path = arg
       elif opt in ("-y", "--style"):
           style = arg
       elif opt in ("-d", "--depthlimit"):
           depthlimit = arg
       elif opt in ("-i", "--itemlimit"):
           itemlimit = arg
       elif opt in ("-b", "--beyond"):
           beyond= arg
       elif opt in ("-s", "--sort"):
           sort = arg
       elif opt in ("-r", "--sort_reverse"):
           sort_reverse = arg

    s = sd.seedir(path=path,
                  style=style,
                  depthlimit=depthlimit,
                  itemlimit=itemlimit,
                  beyond=beyond,
                  sort=sort,
                  sort_reverse=sort_reverse,
                  printout=False)

    print('\n', s, '\n', sep='')

if __name__ == "__main__":
    main()