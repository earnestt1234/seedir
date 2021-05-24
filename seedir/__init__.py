# -*- coding: utf-8 -*-
"""
seedir is a Python package for creating, editing, and reading folder tree
diagrams.

The general logic of seedir is based on representing directories in 3
different forms: real directories on a computer, text diagrams of directories,
and "fake directories" (manipulable Python folder objects). seedir provides
tools for going in between these formats.

.. include:: gettingstarted.md
"""

__pdoc__ = {'command_line' : False}

#imports for package namespace
from .realdir import seedir

from .fakedir import (fakedir,
                      fakedir_fromstring,
                      populate,
                      randomdir,)

from .fakedir import FakeDir as FakeDir
from .fakedir import FakeFile as FakeFile
from .fakedir import FakeItem as FakeItem

from .errors import SeedirError, FakedirError

from .printing import (get_styleargs,
                       STYLE_DICT,
                       words)