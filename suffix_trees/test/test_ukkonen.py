import random
import string

import pytest

from suffix_trees import STree


def canonical(node, word, parent_depth):
    """Canonical, builder-independent representation of a suffix (sub)tree.

    Internal node idx values may legitimately differ between construction
    algorithms (any occurrence of the path label is valid), so only edge
    labels, tree shape and leaf suffix indexes are compared.
    """
    edge = word[node.idx + parent_depth: node.idx + node.depth]
    if node.is_leaf():
        return (edge, node.idx, ())
    children = tuple(sorted(canonical(c, word, node.depth)
                            for c in node.transition_links.values()))
    return (edge, None, children)


@pytest.mark.parametrize("text", [
    "abcabxabcd",
    "aaaaaaa",
    "mississippi",
    "abcdefghab",
    "banana",
    "a",
])
def test_ukkonen_matches_mccreight(text):
    mc = STree.STree(text)
    uk = STree.STree(text, builder="ukkonen")
    assert canonical(uk.root, uk.word, 0) == canonical(mc.root, mc.word, 0)


def test_ukkonen_matches_mccreight_random():
    random.seed(7)
    for n in [10, 50, 200, 1000]:
        for alphabet in ["ab", "abc", string.ascii_lowercase]:
            text = ''.join(random.choice(alphabet) for _ in range(n))
            mc = STree.STree(text)
            uk = STree.STree(text, builder="ukkonen")
            assert canonical(uk.root, uk.word, 0) == canonical(mc.root, mc.word, 0), \
                f"Trees differ for input: {text!r}"


def test_ukkonen_find():
    st = STree.STree("abcdefghab", builder="ukkonen")
    assert st.find("abc") == 0
    assert st.find("xyz") == -1
    assert st.find_all("ab") == {0, 8}


def test_ukkonen_find_random():
    random.seed(11)
    text = ''.join(random.choice("abcd") for _ in range(500))
    st = STree.STree(text, builder="ukkonen")
    for _ in range(100):
        i = random.randint(0, len(text) - 1)
        j = random.randint(i + 1, len(text))
        assert st.find(text[i:j]) == text.find(text[i:j])


def test_ukkonen_gst_lcs():
    a = ["xxxabcxxx", "adsaabc", "ytysabcrew", "qqqabcqw", "aaabc"]
    st = STree.STree(a, builder="ukkonen")
    assert st.lcs() == "abc"


def test_ukkonen_bytes():
    st = STree.STree(b"abcdefghab", builder="ukkonen")
    assert st.find(b"abc") == 0
    assert st.find_all(b"ab") == {0, 8}


def test_invalid_builder():
    with pytest.raises(ValueError):
        STree.STree("abc", builder="nosuchalgorithm")
