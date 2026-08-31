# suffix_trees

![ci](https://github.com/ptrus/suffix-trees/workflows/ci/badge.svg)
[![codecov](https://codecov.io/gh/ptrus/suffix-trees/branch/master/graph/badge.svg)](https://codecov.io/gh/ptrus/suffix-trees)
[![PyPI](https://img.shields.io/pypi/v/suffix-trees)](https://pypi.org/project/suffix-trees/)

Python implementation of Suffix Trees and Generalized Suffix Trees, with the
typical applications built in: substring search (`find`, `find_all`) and
longest common substring of multiple strings (`lcs`, `lcsm`).

Trees are built in linear time: batch construction uses McCreight's algorithm,
online construction uses Ukkonen's.

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

# Online mode (Ukkonen's algorithm): text can be appended incrementally and
# the tree queried between appends.
st = STree.STree(online=True)
st.append("abcab")
print(st.find("bca"))  # 1
st.append("xabcd")
print(st.find("abcd"))  # 6
```

### API

| Method | Description |
| --- | --- |
| `STree(data=None, online=False)` | Builds a suffix tree from a string/bytes, or a generalized suffix tree from a list of them. With `online=True`, `data` (str/bytes only) is the first appended chunk instead. |
| `find(y)` | Starting index of the first occurrence of `y`, or `-1`. |
| `find_all(y)` | Set of starting indexes of all occurrences of `y` (empty set if none). |
| `lcs(stringIdxs=-1)` | Longest common substring of the strings of a generalized suffix tree (optionally restricted to the strings at the given indexes). |
| `lcsm(stringIdxs=-1)` | Like `lcs()`, but returns a sorted list of *all* longest common substrings when several are tied for maximal length. |
| `append(data)` | Online trees only: appends str/bytes to the text, in any chunking. |

Notes on online mode: between appends the tree is the *implicit* suffix tree
of the text so far — `find()` is exact on it, while `find_all()` may miss
occurrences that are suffixes of the current text (they have no leaf yet).
Batch and online construction produce identical trees for the same text.

### Development

The project is managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync            # create venv and install dev dependencies
uv run pytest      # run tests
uv run ruff check  # lint
```
