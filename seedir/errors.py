# -*- coding: utf-8 -*-
"""
Custom exceptions for seedir.

"""

__all__ = ['FakedirError']

# NOTE: SeedirError removed for 0.4.0

# class SeedirError(Exception):
#     """Class for representing errors from module `seedir.realdir`"""

class FakedirError(Exception):
    """Class for handling errors from module `seedir.fakedir`"""
