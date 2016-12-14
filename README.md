# suffix_trees
Python implementation of Suffix Trees and Generalized Suffix Trees. Provided also methods with typcal aplications of STrees and GSTrees. 

### Usage

```python
from suffix_trees import STree

# Suffix-Tree example.
st = STree.STree("abcdefghab")
print(st.find("abc")) # 0
print(st.find_all("ab")) # [0, 8]

# Generalized Suffix-Tree example.
a = ["xxxabcxxx", "adsaabc", "ytysabcrew", "qqqabcqw", "aaabc"]
st = STree.STree(a)
print(st.lcs()) # "abc"
```

