#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

from .realdir import seedir

helptxt = """
Help for the seedir CLI.  Function for printing a folder tree
structure, similar to UNIX `tree`.  Directs all arguments to `seedir.seedir()`.

Note that this has been revamped for version v0.3.1.  Specifically, parsing
was moved from getopts to argparse.  Options should now all explicitly
reference parameters of `seedir.seedir()`.

Not all seedir arguments are accepted, namely ones which expect Python
callables and ones which alter the style.  The latter may be added
in a future version.

Options (short/long):

    -b / --beyond BEYOND
        Way to represent items past the depthlimit or itemlimit.
        Options are 'content', 'ellipsis', or explicit string starting
        with an underscore.  Not set by default.

    -d / --depthlimit DEPTHLIMIT
        Integer limit on depth of folders to enter. Default: None

    -f / --first FIRST
        Sort the directory so that either files or folders appear first.
        Options are "folders" or "files".

    -h / --help
        Show this message and exit.

    -i / --itemlimit ITEMLIMIT
        Integer limit on the number of items to include per directory.
        Default: None

    -p / --path PATH
        Dir to see.  Default: current directory (os.getcwd())

    -r / --sort_reverse
        Reverse the sort.

    -s / --sort
        Sort the contents of each directory by name.

    -t / --indent INDENT
        Amount to indent.  Default: 2

    -y / --style STYLE
        seedir style to use.  Default: "lines"

Options (long only):

    --include_folders, --include_files, --exclude_folders, --exclude_files ...
        Folder / file names to include or exclude.  Not set by default. Pass
        multiple items as space-separated values.

    --regex
        Interpret include/exclude folder/file arguments as Python regex.
"""

def parse():

    """Parse command line arguments with argparse."""

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-b', '--beyond', default=None)
    parser.add_argument('-d', '--depthlimit', default=None, type=int)
    parser.add_argument('-f', '--first', default=None)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-i', '--itemlimit', default=None, type=int)
    parser.add_argument('-p', '--path', default=os.getcwd())
    parser.add_argument('-r', '--sort_reverse', action='store_true')
    parser.add_argument('-s', '--sort', action='store_true')
    parser.add_argument('-t', '--indent', default=2, type=int)
    parser.add_argument('-y', '--style', default='lines')

    parser.add_argument('--include_folders', default=None, nargs='+')
    parser.add_argument('--exclude_folders', default=None, nargs='+')
    parser.add_argument('--include_files', default=None, nargs='+')
    parser.add_argument('--exclude_files', default=None, nargs='+')
    parser.add_argument('--regex', action='store_true')

    return parser.parse_args()

def main():

    """Parses arguments and passes them to `seedir.seedir()`"""

    args = parse()
    if args.help:
        print(helptxt)
        return

    kwargs = vars(args)
    del kwargs['help']
    seedir(**kwargs)

if __name__ == '__main__':
    main()

