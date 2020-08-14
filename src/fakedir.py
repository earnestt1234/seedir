# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:13:02 2020

@author: earne
"""
class FakedirError(Exception):
    """Class for handling errors from fakedir"""

class File:
    def __init__(self, name, root='', ext='.txt', depth=0):
        self.name = name
        self.ext = ext
        self.filename = name + ext
        self.root = root
        if not root:
            self.path = root + '/' + self.filename
        else:
            self.path = self.filename
        self.depth = depth

class Folder:
    def __init__(self, name, root='', depth=0):
        self.name = name
        self.root = root
        if not root:
            self.path = root + '/' + self.name
        else:
            self.path = self.name
        self.depth = depth
        self.children = []

    def create_folder(self, name):
        self.children.append(Folder(name, self.path, depth=self.depth + 1))

    def create_file(self, name, ext='.txt'):
        self.children.append(File(name, self.path, depth=self.depth + 1))

def populate(folder, depth=3, subfolders=2, subfiles=2):
    for i in range(subfiles):
        folder.create_file('FILE')
    for i in range(subfolders):
        folder.create_folder('FOLDER')
    for f in folder.children:
        if isinstance(f, Folder):
            if f.depth <= depth:
                populate(f, subfolders, subfiles)

def fakedir(depth=3, files=2, folders=2):
    top = Folder('Folder0')
    populate(top, depth, subfolders=folders, subfiles=files)
    return top

x = fakedir()