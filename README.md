# seedir
A Python package for creating, editing, and reading folder tree diagrams.

![](https://raw.githubusercontent.com/earnestt1234/seedir/master/img/pun.jpg)

*Photo by [Adam Kring](https://unsplash.com/@adamkring).*


```python
>>> import seedir as sd
>>> sd.seedir(style='lines', itemlimit=10, depthlimit=2, exclude_folders='.git')
seedir/
├─.gitattributes
├─.gitignore
├─.ipynb_checkpoints/
│ └─examples-checkpoint.ipynb
├─build/
│ ├─bdist.win-amd64/
│ └─lib/
├─CHANGELOG.md
├─dist/
│ └─seedir-0.1.4-py3-none-any.whl
├─docs/
│ ├─exampledir/
│ ├─gettingstarted.md
│ ├─seedir/
│ └─templates/
├─img/
│ ├─pun.jpg
│ ├─seedir_diagram.png
│ └─seedir_diagram.pptx
├─LICENSE
└─MANIFEST.in

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

