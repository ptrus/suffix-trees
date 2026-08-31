# suffix_trees

![ci](https://github.com/ptrus/suffix-trees/workflows/ci/badge.svg)
[![codecov](https://codecov.io/gh/ptrus/suffix-trees/branch/master/graph/badge.svg)](https://codecov.io/gh/ptrus/suffix-trees)
[![PyPI](https://img.shields.io/pypi/v/suffix-trees)](https://pypi.org/project/suffix-trees/)

Python implementation of Suffix Trees and Generalized Suffix Trees. Also provided methods with typical applications of STrees and GSTrees.

### Installation

```bash
pip install suffix-trees
```

Requires Python 3.9+ and has no dependencies.

### Usage

```python
from suffix_trees import STree

# Suffix-Tree example.
st = STree.STree("abcdefghab")
print(st.find("abc"))  # 0
print(st.find_all("ab"))  # {0, 8}

# Generalized Suffix-Tree example.
a = ["xxxabcxxx", "adsaabc", "ytysabcrew", "qqqabcqw", "aaabc"]
st = STree.STree(a)
print(st.lcs())  # "abc"

# lcsm() returns all longest common substrings when there are ties.
a = ["klexxxabc", "kleyyyabc"]
st = STree.STree(a)
print(st.lcsm())  # ["abc", "kle"]

# bytes input works too (find/find_all/lcs/lcsm then accept and return bytes).
st = STree.STree(b"abcdefghab")
print(st.find(b"abc"))  # 0

# The construction algorithm can be chosen explicitly:
# McCreight (default) or Ukkonen. Both are O(n) and build identical trees.
st = STree.STree("abcdefghab", builder="ukkonen")
print(st.find("abc"))  # 0
```

### Development

The project is managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync            # create venv and install dev dependencies
uv run pytest      # run tests
uv run ruff check  # lint
```
