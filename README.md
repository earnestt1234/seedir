# seedir
A Python package for creating, editing, and reading folder tree diagrams.

![](https://raw.githubusercontent.com/earnestt1234/seedir/master/img/pun.jpg)

*Photo by [Adam Kring](https://unsplash.com/@adamkring).*


```python
>>> import seedir as sd
>>> sd.seedir(style='lines', itemlimit=10, depthlimit=2, exclude_folders='.git')

seedir/
├─.DS_Store
├─seedirpackagetesting.py
├─LICENSE
├─tests/
│ ├─__init__.py
│ ├─__pycache__/
│ └─tests.py
├─MANIFEST.in
├─pdoc_command.txt
├─docs/
│ └─seedir/
├─README.md
├─img/
│ └─pun.jpg
└─setup.py
```

## Installation

Available with [`pip`](https://pypi.org/project/seedir/):

```
pip install seedir
```

## Usage

See the [API documentation](https://earnestt1234.github.io/seedir/seedir/index.html) (generated with [pdoc3](https://pdoc3.github.io/pdoc/)).

## License

Open source under MIT.

