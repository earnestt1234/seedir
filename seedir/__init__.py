# -*- coding: utf-8 -*-
"""
[seedir](https://github.com/earnestt1234/seedir) is a Python package for
creating, editing, and reading folder tree diagrams.

The general logic of seedir is based on representing directories in 3
different forms: real directories on a computer, text diagrams of directories,
and "fake directories" (manipulable Python folder objects). seedir provides
tools for going in between these formats.

.. include:: ../docs/gettingstarted.md

## Cheatsheet

![](https://raw.githubusercontent.com/earnestt1234/seedir/master/img/seedir_diagram.png)

"""

#imports for package namespace
from .realdir import seedir

from .fakedir import (fakedir,
                      fakedir_fromstring,
                      populate,
                      randomdir,)

from .fakedir import FakeDir
from .fakedir import FakeFile

from .printing import (get_styleargs,
                       STYLE_DICT,)
