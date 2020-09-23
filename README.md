# seedir
A Python package for creating, editing, and reading folder tree diagrams.

<p align="center">
	<img src="img/pun.jpg" width="500">
</p>

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

Available with `pip`:

```
pip install seedir
```

## Usage

See the `seedir` Jupyter Notebook for guided examples, or the documentation (coming soon!).

## License

Open source under MIT.

