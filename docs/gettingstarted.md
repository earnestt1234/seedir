# Getting started

The following examples will cover what you can do with seedir.  We can start by importing the package with the `sd` alias:

```python
>>> import seedir as sd

```

## Displaying folder trees

The primary function of seedir is to create plain text diagrams of folders, for use in blogs, examples, Q&As, etc.  The GitHub repo for seedir includes an example folder (`seedir/seedir/exampledir`) which will be used here.

To printout out the structure of this folder, you can use the primary `seedir.realdir.seedir()` function:

```python
>>> path = 'exampledir'
>>> sd.seedir(path)
exampledir/
├─scrooge/
│ ├─patrimonial/
│ ├─sandal/
│ ├─light.pdf
│ ├─paycheck/
│ │ ├─electrophoresis.txt
│ │ └─Pyongyang/
│ └─reliquary.pdf
├─jowly.pdf
├─monkish.txt
├─Uganda/
├─pedantic/
│ └─cataclysmic.txt
└─Vogel.txt
  
```

By default, **the output is printed**.  To return a string instead, use the `printout` argument:

```python
>>> s = sd.seedir(path, printout=False)
>>> print(type(s))
<class 'str'>

```

## Trimming folder trees

Sometimes a directory is too large, is private, or contains certain irrelevant files.  To handle this, there are a few arguments which allow you to edit the items included in the output.  

### Including & excluding folders & files

One way is to call out specific folders of files to include or exclude:

```python
>>> sd.seedir(path, include_folders=['scrooge','paycheck'], exclude_files='reliquary.pdf')
exampledir/
├─scrooge/
│ ├─light.pdf
│ └─paycheck/
│   └─electrophoresis.txt
├─jowly.pdf
├─monkish.txt
└─Vogel.txt

```

These "include" and "exclude" arguments also support regular expressions:

```python
>>> sd.seedir(path, include_files='.*\.pdf$', regex=True) # all PDFs
exampledir/
├─scrooge/
│ ├─patrimonial/
│ ├─sandal/
│ ├─light.pdf
│ ├─paycheck/
│ │ └─Pyongyang/
│ └─reliquary.pdf
├─jowly.pdf
├─Uganda/
└─pedantic/

```

### Masking

You can also use the `mask` parameter to functionally filter out items in the folder. Pathnames are passed to the mask function, and items are kept if `True` is returned:

```python
>>> import os

>>> def foo(x): # omits folders with more than 2 items
... 	if os.path.isdir(x) and len(os.listdir(x)) > 2:
... 		return False
... 	return True

>>> sd.seedir(path, mask=foo)
exampledir/
├─jowly.pdf
├─monkish.txt
├─Uganda/
├─pedantic/
│ └─cataclysmic.txt
└─Vogel.txt

```

### Limiting the depth or number of items

You can also wholly limit the output by providing the `depthlimit` or `itemlimit` arguments. Respectively, these arguments limit the depth of folders to enter and the number of items to include per folder.  

```python
>>> sd.seedir(path, depthlimit=1)
exampledir/
├─scrooge/
├─jowly.pdf
├─monkish.txt
├─Uganda/
├─pedantic/
└─Vogel.txt

>>> sd.seedir(path, itemlimit=3)
exampledir/
├─scrooge/
│ ├─patrimonial/
│ ├─sandal/
│ └─light.pdf
├─jowly.pdf
└─monkish.txt

```

As `seedir.realdir.seedir()` uses recursion, these arguments can hedge the traversal of deep, complicated folders.

When limiting the tree, using the `beyond` argument can be helpful to show what is being cut. The special value `'content'` shows the number of folders and files:

```python
>>> sd.seedir(path, depthlimit=1, beyond='content')
exampledir/
├─scrooge/
│ └─3 folder(s), 2 file(s)
├─jowly.pdf
├─monkish.txt
├─Uganda/
│ └─0 folder(s), 0 file(s)
├─pedantic/
│ └─0 folder(s), 1 file(s)
└─Vogel.txt

```

### Sorting

Especially when using the `itemlimit`, but also generally, you may want to sort the output to determine which items appear first. You can apply a general sort using `sort=True`:

```python
>>> sd.seedir(path, itemlimit=5, sort=True)
exampledir/
├─Uganda/
├─Vogel.txt
├─jowly.pdf
├─monkish.txt
└─pedantic/
  └─cataclysmic.txt
  
```

There are additional reverse and key arguments (akin to `sorted()` or `list.sort()`) which allow you to customize the sorting:

```python
>>> sd.seedir(path, itemlimit=5, sort=True, sort_reverse=True, sort_key=lambda s : len(s))
exampledir/
├─monkish.txt
├─jowly.pdf
├─Vogel.txt
├─pedantic/
│ └─cataclysmic.txt
└─scrooge/
  ├─reliquary.pdf
  ├─patrimonial/
  ├─light.pdf
  ├─paycheck/
  │ ├─electrophoresis.txt
  │ └─Pyongyang/
  └─sandal/
  
```

The `first` argument allows you to select whether files or folders appear first:

```python
>>> sd.seedir(path, itemlimit=5, first='files')
exampledir/
├─Vogel.txt
├─jowly.pdf
├─monkish.txt
├─Uganda/
└─pedantic/
  └─cataclysmic.txt
  
```

## Styles 💅

`seedir.realdir.seedir()` has a few builtin styles for formatting the output of the folder tree:

```python
>>> sd.seedir(path, itemlimit=3, style='emoji')
📁 exampledir/
├─📁 scrooge/
│ ├─📁 patrimonial/
│ ├─📁 sandal/
│ └─📄 light.pdf
├─📄 jowly.pdf
└─📄 monkish.txt

```

For any builtin style, you can customize the indent size:

```python
>>> sd.seedir(path, itemlimit=3, style='spaces', indent=4)
exampledir/
    scrooge/
        patrimonial/
        sandal/
        light.pdf
    jowly.pdf
    monkish.txt
    
>>> sd.seedir(path, itemlimit=3, style='plus', indent=6)
exampledir/
+-----scrooge/
|     +-----patrimonial/
|     +-----sandal/
|     +-----light.pdf
+-----jowly.pdf
+-----monkish.txt

```

Each style is basically a collection of string "tokens" which are combined to form the header of each printed line (based on the depth and folder structure). You can see these tokens using `seedir.printing.get_styleargs()`:

```python
>>> sd.get_styleargs('emoji')
{'split': '├─', 'extend': '│ ', 'space': '  ', 'final': '└─', 'folderstart': '📁 ', 'filestart': '📄 '}
 
```

You can pass any of these tokens as `**kwargs` to explicitly customize styles with new symbols (note that passed tokens will not be affected by the `indent` parameter; it assumes you know how long you want them to be):

```python
>>> sd.seedir(path, itemlimit=3, space='  ', extend='||', split='-}', final='\\\\', folderstart=' ', filestart=' ')
exampledir/
-} scrooge/
||-} patrimonial/
||-} sandal/
||\\ light.pdf
-} jowly.pdf
\\ monkish.txt

```

There are also `uniform` and `anystart` arguments for customizing multiple tokens at once:

```python
>>> sd.seedir(path, itemlimit=3, uniform='----', anystart='>')
>exampledir/
---->scrooge/
-------->patrimonial/
-------->sandal/
-------->light.pdf
---->jowly.pdf
---->monkish.txt

```

## Fake directories

You can also create or edit directory examples by using "fake directories" in `seedir`. These are Python representations of folders and files, which can be manipulated in ways similar to real directories.

### Making from scratch

`seedir.fakedir.FakeDir` is a folder class; you can be used to initialize an example folder tree.   `FakeDir` objects have a `seedir.fakedir.FakeDir.seedir()` method, which is fundamentally similar to `seedir.realdir.seedir()` for real system paths:

```python
>>> x = sd.FakeDir('myfakedir')
>>> x.seedir()
myfakedir/

```

To add items to `x`, you can create subitems, initialize new directories, or move existing ones:

```python
>>> x.create_file(['__init__.py', 'main.py', 'styles.txt'])
>>> x.create_folder('docs')

>>> y = sd.FakeDir('resources', parent=x)

>>> z = sd.FakeDir('images')
>>> z.parent = y

>>> for n in ['a', 'b', 'c']:
...     z.create_file(n + '.png')

>>> x.seedir(sort=True, first='folders')
myfakedir/
├─docs/
├─resources/
│ └─images/
│   ├─a.png
│   ├─b.png
│   └─c.png
├─__init__.py
├─main.py
└─styles.txt

```

You can use path-like strings to index fake directories:

```python
>>> x['resources/images/a.png']
FakeFile(myfakedir/resources/images/a.png)

```

You can also use the `listdir` or `get_child_names` methods to get the children of a folder (or their names):

```python
>>> x['resources/images'].listdir()
[FakeFile(myfakedir/resources/images/a.png), FakeFile(myfakedir/resources/images/b.png), FakeFile(myfakedir/resources/images/c.png)]

>>> x['resources/images'].get_child_names()
['a.png', 'b.png', 'c.png']

```

You can use the `delete` method to remove items by name or by object:

```python
>>> x['resources/images'].delete([x['resources/images/a.png'], 'b.png'])
>>> x.seedir()
myfakedir/
├─__init__.py
├─main.py
├─styles.txt
├─docs/
└─resources/
  └─images/
    └─c.png

```

You can also move items within the tree:

```python
>>> x['styles.txt'].parent = x['resources']
>>> x.seedir()
myfakedir/
├─__init__.py
├─main.py
├─docs/
└─resources/
  ├─images/
  │ └─c.png
  └─styles.txt
  
```

### Turn existing directories into fakes

The `seedir.fakedir.fakedir()` function allows you to convert real directories into `seedir.fakedir.FakeDir` objects:

```python
>>> f = sd.fakedir(path) # using path from above
>>> f.seedir()
exampledir/
├─scrooge/
│ ├─patrimonial/
│ ├─sandal/
│ ├─light.pdf
│ ├─paycheck/
│ │ ├─electrophoresis.txt
│ │ └─Pyongyang/
│ └─reliquary.pdf
├─jowly.pdf
├─monkish.txt
├─Uganda/
├─pedantic/
│ └─cataclysmic.txt
└─Vogel.txt

>>> type(f)
<class 'seedir.fakedir.FakeDir'>

```

Similar to `seedir.realdir.seedir()`, `seedir.fakedir.fakedir()` has options to limit the incoming folders and files:

```python
>>> f = sd.fakedir(path, exclude_folders='scrooge', exclude_files='Vogel.txt')
>>> f.seedir()
exampledir/
├─jowly.pdf
├─monkish.txt
├─Uganda/
└─pedantic/
  └─cataclysmic.txt
  
```

Fake directories created from your system directories can be combined with other ones created from scratch:

```python
>>> f.parent = x
>>> x.seedir()
myfakedir/
├─__init__.py
├─main.py
├─docs/
├─resources/
│ ├─images/
│ │ └─c.png
│ └─styles.txt
└─exampledir/
  ├─jowly.pdf
  ├─monkish.txt
  ├─Uganda/
  └─pedantic/
    └─cataclysmic.txt

```

### Creating folder trees from text

The `seedir.fakedir.fakedir_fromstring()` method allows you to read in existing folder tree diagrams. Given this:

```python
somedir/
  - folder1
  - folder2
  - folder3
    - file1
    - file2
    - subfolder
      - subfolder
        - deepfile
  - folder4
```

You can do:

```python
>>> s = '''somedir/
...   - folder1
...   - folder2
...   - folder3
...     - file1
...     - file2
...     - subfolder
...       - subfolder
...         - deepfile
...   - folder4'''

>>> g = sd.fakedir_fromstring(s)
>>> g.seedir()
somedir/
├─folder1
├─folder2
├─folder3/
│ ├─file1
│ ├─file2
│ └─subfolder/
│   └─subfolder/
│     └─deepfile
└─folder4

```

This can be used to read in examples found online.  [For instance](https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html):

```python
>>> s = '''test/                      # root folder
...     packA/                 # package packA
...         subA/              # subpackage subA
...             __init__.py
...             sa1.py
...             sa2.py
...         __init__.py
...         a1.py
...         a2.py
...     packB/                 # package packB (implicit namespace package)
...         b1.py
...         b2.py
...     math.py
...     random.py
...     other.py
...     start.py'''

>>> h = sd.fakedir_fromstring(s, parse_comments=True) # handling the added comments
>>> h.seedir(style='emoji')
📁 test/
├─📁 packA/
│ ├─📁 subA/
│ │ ├─📄 __init__.py
│ │ ├─📄 sa1.py
│ │ └─📄 sa2.py
│ ├─📄 __init__.py
│ ├─📄 a1.py
│ └─📄 a2.py
├─📁 packB/
│ ├─📄 b1.py
│ └─📄 b2.py
├─📄 math.py
├─📄 random.py
├─📄 other.py
└─📄 start.py

```

This function has not been extensively tested, so expect failures/misreadings!

### Creating random directories

You can also use seedir to create randomly generated directories.

```python
>>> r = sd.randomdir(seed=4.21, extensions=['png', 'jpg', 'pdf'], name='sorandom')
>>> r.seedir()
sorandom/
├─plethora.pdf
├─randy.jpg
├─giddap.pdf
├─adage/
└─Gobi/
  ├─inventive.pdf
  ├─Noel.jpg
  ├─archaic/
  │ └─bream.pdf
  ├─salve/
  └─NY/
    └─Bahrein.jpg
    
```

Additional parameters dictate the size of the tree created:

```python
>>> sd.randomdir(files=range(5), # making an unnecessarily large tree
...              folders=[1,2],
...              stopchance=.3,
...              depth=5,
...              extensions=['png', 'jpg', 'pdf'],
...              seed=4.21).seedir()
MyFakeDir/
├─plethora.pdf
├─randy.jpg
├─giddap.pdf
├─adage.jpg
├─oint/
│ ├─inventive.pdf
│ ├─Noel.jpg
│ ├─archaic.pdf
│ ├─NY/
│ │ ├─neonatal.png
│ │ ├─pyknotic.png
│ │ ├─wife.png
│ │ ├─Mickelson/
│ │ │ └─Caruso/
│ │ │   ├─royal.pdf
│ │ │   ├─aurora.pdf
│ │ │   ├─stampede.pdf
│ │ │   ├─divan.pdf
│ │ │   └─Coffey/
│ │ │     ├─sad.pdf
│ │ │     ├─cob.pdf
│ │ │     ├─natural.jpg
│ │ │     ├─skinflint.pdf
│ │ │     └─exploration/
│ │ └─Westchester/
│ │   ├─metamorphism.jpg
│ │   ├─Pulitzer.jpg
│ │   ├─permissive.png
│ │   ├─wakerobin/
│ │   │ ├─talon.jpg
│ │   │ ├─peace.pdf
│ │   │ ├─drowse.jpg
│ │   │ ├─rutabaga/
│ │   │ └─silage/
│ │   │   ├─pert.png
│ │   │   ├─defensible.png
│ │   │   ├─lexicon.png
│ │   │   ├─eureka.pdf
│ │   │   └─impasse/
│ │   └─calve/
│ │     ├─superstitious.png
│ │     └─embroider/
│ │       ├─safekeeping.pdf
│ │       ├─brig.png
│ │       ├─systemic.pdf
│ │       ├─caddis.png
│ │       └─borosilicate/
│ └─Pentecost/
│   ├─visceral.pdf
│   ├─replica.png
│   ├─rockaway.jpg
│   ├─luxe.jpg
│   └─breath/
│     ├─contain.jpg
│     └─homophobia/
│       ├─crewman.jpg
│       └─restroom/
└─joss/
  ├─Technion.jpg
  ├─Mynheer.png
  ├─begonia/
  └─Djakarta/
    ├─Lionel.png
    ├─Cantonese.pdf
    ├─drafty.jpg
    ├─half/
    │ └─builtin/
    │   ├─ermine.jpg
    │   └─Cretan/
    │     ├─happenstance.pdf
    │     ├─insoluble.jpg
    │     ├─Audrey/
    │     └─octennial/
    └─recipient/
      ├─splintery.jpg
      ├─bottom.png
      ├─stunk.png
      ├─Polyhymnia/
      └─Holocene/
        ├─plaque.pdf
        ├─westerly.png
        ├─glassine.jpg
        ├─titanium.pdf
        └─square/
        
```

### Turning fake directories into real ones

Finally, there is a `seedir.fakedir.FakeDir.realize()` method which can covert fake directories into real folders on your computer.

```
x = sd.randomdir()
x.realize(path='where/to/create/it/')
```

All files created will be empty.