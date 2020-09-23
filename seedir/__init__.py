# -*- coding: utf-8 -*-
"""
seedir is a Python package for creating, editing, and reading folder tree
diagrams.

The general logic of seedir is based on representing directories in 3
different forms:

    1. Real directories on a computer
    2. Text diagrams of directories
    3. Coded, editable representations of folder trees (or "fake directories")

seedir provides tools for going in between these formats.

@author: Tom Earnest

GitHub: https://github.com/earnestt1234/seedir
"""

#imports for package namespace
from .seedir import (recursive_folder_structure,
                     seedir)

from .fakedir import (FakeDir,
                      FakeFile,
                      FakeItem,
                      fakedir,
                      fakedir_fromstring,
                      populate,
                      randomdir,
                      recursive_add_fakes,
                      recursive_fakedir_structure,
                      sort_fakedir)

from .errors import SeedirError, FakedirError

from .printing import (format_indent,
                       get_styleargs,
                       is_match,
                       STYLE_DICT,
                       words)