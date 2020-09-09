# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 11:53:42 2020

@author: earne
"""

from .seedir import (count_files,
                     count_folders,
                     recursive_folder_structure,
                     seedir,
                     sort_dir)
from .fakedir import (count_fakedirs,
                      count_fakefiles,
                      FakeDir,
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