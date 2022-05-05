# Changelog

This document will serve as a record for past and future changes to seedir.  It is being retroactively added after the version [0.2.0](https://github.com/earnestt1234/seedir/releases/tag/v0.2.0) release (so notes for prior releases will be less detailed).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 0.3.1 - PLANNED

- Update the `formatter` parameter to edit additional arguments, besides style keywords
- Add `folderend` and `fileend` parameters for customizing tokens at end of items
- Clean up the command line tool.
- See the "dev" branch for tracking progress

## [0.3.0](https://github.com/earnestt1234/seedir/releases/tag/v0.3.0) - 2021-12-20

### Added

- [`formatter` parameter](https://github.com/earnestt1234/seedir/issues/4) for more customizable diagrams
- FakeDir methods for creating files/folders now return references to the objects created
- A `copy()` method for FakeDirs
- A `siblings()` method for FakeDirs

### Changed

- Documentation updates
  - Added code blocks to examples in docstrings
  - replaced the "cheatsheet.png" image in the Getting Started section with a markdown link
  - remove broken link to `FolderStructure` class in `seedir.realdir` module
  - fixed some examples in docstrings and readmes
- in getting started, redo examples to omit empty folders (which are omitted by GitHub)
- replace `'\s'` with `' '` in `seedir.fakedir.fakedir_fromstring()`
- [Remove .DS_Store files](https://github.com/earnestt1234/seedir/pull/5) (thanks @[timweissenfels](https://github.com/timweissenfels))
- Reverted API doc style back to pdoc3 default

### Fixed

- remove [call to `copy` method](https://github.com/earnestt1234/seedir/blob/09fbed86a356fa9b01588546e1e7dbda15812b49/seedir/fakedir.py#L417) in `Fakedir.delete()`, which prevented non-list arguments
- the `walk_apply` method is now applied to the calling folder, rather than just children

## [0.2.0](https://github.com/earnestt1234/seedir/releases/tag/v0.2.0) - 2021-05-21

### Added

- a new `folderstructure.py` module was added containing a single folder tree construction algorithm.  This module is called for both real directories (`seedir.realdir.seedir()`) and fake directories (`seedir.fakedir.Fakedir.seedir()`).  The code was also refactored to be less convoluted and more readable (and also more correct for some fringe cases)
  - using `depthlimit=0` with a `beyond` string now produces just the root folder (this was incorrect before)
  - with `beyond='content'`, empty folders are only shown when the `depthlimit` is crossed
  - trailing separators or slashes no longer cause the name of the root folder to be empty
- A `folderstructurehelpers.py` module was also added to support the main folder structure algorithm.
- More unit tests were added.
- `name` parameter added to `seedir.fakedir.randomdir`
- Convert some arguments to `bool` or `int` in the command line tool

### Changed

- The documentation was overhauled:
  - The Jupyter Notebook examples file was removed, in favor of a `gettingstarted.md` file which is included in the main page of the API docs.
  - The getting started README as well as the `seedir.fakedir` module are now `doctest`-able.
  - New style added to the API docs.
  - `seedir.seedir` module has been renamed to `seedir.realdir` to avoid some of my confusions
  - added an `exampledir` to the `docs` folder for some examples
- Some changes to `seedir.fakedir.fakedir_fromstring` to handle some more failed cases.
- `words`, `FakeItem` removed from package namespace

## [0.1.4](https://github.com/earnestt1234/seedir/releases/tag/v0.1.4) - 2021-03-01

### Added

- Documentation was updated to include code formatting and within-package hyperlinks (thanks to pdoc)

### Changed

- the variable name of the output of `seedir.seedir()` and `seedir.fakedir()` was renamed from `rfs` to `s`

## [0.1.3](https://github.com/earnestt1234/seedir/releases/tag/v0.1.3) - 2020-12-31

### Changed

- Code block examples added to docstrings, following [this issue](https://github.com/earnestt1234/seedir/issues/3)

## [0.1.2](https://github.com/earnestt1234/seedir/releases/tag/v0.1.2) - 2020-11-28

### Added

- [new `mask` parameter](https://github.com/earnestt1234/seedir/issues/1) for functionally filtering items, used by `seedir.seedir`, `seedir.FakeDir.seedir`, and `seedir.fakedir`
- test cases for the `mask` parameter

### Changed

- Updated examples notebook
- Updated documentation

## [0.1.1](https://github.com/earnestt1234/seedir/releases/tag/v0.1.1) - 2020-11-20

Initial public release of seedir 🎉