# suffix_trees
Python implementation of Suffix Trees and Generalized Suffix Trees. Also provided methods with typcal applications of STrees and GSTrees. 

Extended from https://github.com/ptrus/suffix-trees to provide extra functionalities.

### Added funcitonalities
1. Find all the common substrings among given strings.
   For example, with lcs[Longest Common Substring],
   ```python
   from suffix_trees.STree import STree
   st = STree(['abcabcabc', 'abc'])
   print(st.lcs(return_str=False)) # "(0, 3)"
   ```
   you'll get the match (0, 3) [starts at 0 and ends at 3 in the first string]
   But it also appears at (4, 7), and (8, 11), right?
   What if you want to have these results as well?
   Here is where this extension comes in.

   With newly added Stree.find_matching_blocks() function,
   you can retrieve more variable common substrings.
   Since it has various options, it has a potential to provide you various common substrings.
   ```python
   from suffix_trees.STree import STree

   st = STree(['abcabcabc', 'abc'])
   print(st.find_matching_blocks(return_str=False, remove_redundant=True, include_duplite=True))
   # [match(start=0, end=3, length=3), match(start=3, end=6, length=3), match(start=6, end=9, length=3)]

   print(st.find_matching_blocks(return_str=False, remove_redundant=True, include_duplite=False))
   # [match(start=0, end=3, length=3)]

   print(st.find_matching_blocks(return_str=False, remove_redundant=False, include_duplite=False))
   # [match(start=0, end=3, length=3), match(start=1, end=3, length=2), match(start=2, end=3, length=1)]
   ```

   Also, if you supply 'abcxabcd' and 'abczabcd', lcs funciton will return 'abcd'.
   But with this function, it is also possible to get 'abc' as well.
   ```python
   from suffix_trees.STree import STree

   st = STree(['abcxabcd', 'abczabcd'])

   print(st.find_matching_blocks(remove_redundant=True, include_duplicate=False))
   # [match(start=4, end=8, length=4), match(start=0, end=3, length=3)]

   print(st.find_matching_blocks(remove_redundant=True, include_duplicate=True))
   # [match(start=4, end=8, length=4), match(start=0, end=3, length=3), match(start=4, end=7, length=3)]
   ```


2. Option to return indices of matches, not the actual strings


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
