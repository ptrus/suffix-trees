import random

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as hs

from suffix_trees import STree

# The first terminal symbol build() uses. Appending it to an online tree turns
# the implicit suffix tree into the true suffix tree of the text, making it
# structurally comparable to a batch-built tree.
TERMINAL = chr(0xE000)


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


def streamed(text, cuts=()):
    """Builds an online tree by appending text in the chunks defined by cuts."""
    st = STree.STree(online=True)
    prev = 0
    for c in sorted(cuts):
        st.append(text[prev:c])
        prev = c
    st.append(text[prev:])
    return st


def test_online_basic():
    st = STree.STree(online=True)
    st.append("abcab")
    assert st.find("bca") == 1
    assert st.find("abd") == -1
    st.append("xabcd")
    assert st.find("bxa") == 4
    assert st.find("abcd") == 6
    assert st.find_all("abc") == {0, 6}


def test_online_constructor_data():
    st = STree.STree("abcab", online=True)
    assert st.find("bca") == 1
    st.append("xabcd")
    assert st.find("abcd") == 6


def test_online_queries_between_appends():
    random.seed(3)
    text = ''.join(random.choice("abc") for _ in range(300))
    st = STree.STree(online=True)
    for i, c in enumerate(text):
        st.append(c)
        prefix = text[:i + 1]
        for _ in range(5):
            a = random.randint(0, i)
            b = random.randint(a + 1, i + 1)
            y = prefix[a:b]
            assert st.find(y) == prefix.find(y)
        assert st.find(prefix[-min(5, len(prefix)):] + "z") == -1


@pytest.mark.parametrize("text", [
    "abcabxabcd",
    "aaaaaaa",
    "mississippi",
    "abcdefghab",
    "banana",
    "a",
])
def test_online_matches_batch(text):
    uk = streamed(text)
    uk.append(TERMINAL)
    mc = STree.STree(text)
    assert canonical(uk.root, uk.word, 0) == canonical(mc.root, mc.word, 0)


def test_online_bytes():
    st = STree.STree(online=True)
    st.append(b"abc")
    st.append(b"def")
    assert st.find(b"cd") == 2
    assert st.find(b"fg") == -1


def test_append_requires_online():
    st = STree.STree("abc")
    with pytest.raises(ValueError):
        st.append("d")


def test_online_rejects_list_input():
    with pytest.raises(ValueError):
        STree.STree(["ab", "cd"], online=True)


def test_build_on_online_tree_raises():
    st = STree.STree(online=True)
    st.append("abc")
    with pytest.raises(ValueError):
        st.build("def")


# -- Hypothesis property tests, covering both builders ------------------------

# Small alphabets force repeated substrings (deep trees, many splits); the
# unicode variant stays below U+E000 so it cannot collide with terminal
# symbols.
texts = hs.one_of(
    hs.text(alphabet="ab", max_size=60),
    hs.text(alphabet="abcd", max_size=120),
    hs.text(alphabet=hs.characters(max_codepoint=0xDFFF,
                                   exclude_categories=('Cs',)),
            max_size=80),
)


def draw_query(data, text):
    """Draws either a substring of text or a short arbitrary string."""
    if text and data.draw(hs.booleans()):
        i = data.draw(hs.integers(0, len(text) - 1))
        j = data.draw(hs.integers(i + 1, len(text)))
        return text[i:j]
    return data.draw(hs.text(alphabet="abcd", min_size=1, max_size=5))


@settings(deadline=None)
@given(hs.data())
def test_hyp_online_structure_matches_batch(data):
    text = data.draw(texts)
    # STree("") historically skips building altogether, so the comparison is
    # only meaningful for non-empty text.
    assume(text)
    cuts = data.draw(hs.lists(hs.integers(0, len(text)), max_size=8))
    uk = streamed(text, cuts)
    uk.append(TERMINAL)
    mc = STree.STree(text)
    assert canonical(uk.root, uk.word, 0) == canonical(mc.root, mc.word, 0)


@settings(deadline=None)
@given(hs.data())
def test_hyp_find_matches_str_find_both_builders(data):
    text = data.draw(texts)
    y = draw_query(data, text)
    mc = STree.STree(text) if text else STree.STree()
    uk = streamed(text)  # implicit tree: find() is exact on it
    assert mc.find(y) == text.find(y)
    assert uk.find(y) == text.find(y)


@settings(deadline=None)
@given(hs.data())
def test_hyp_find_all_matches_bruteforce_both_builders(data):
    text = data.draw(texts)
    y = draw_query(data, text)
    expected = {i for i in range(len(text)) if text.startswith(y, i)}
    mc = STree.STree(text) if text else STree.STree()
    uk = streamed(text)
    uk.append(TERMINAL)  # explicit tree: find_all() is exact on it
    assert mc.find_all(y) == expected
    assert uk.find_all(y) == expected


def brute_common_substrings(strings, length):
    first = strings[0]
    return {first[i:i + length]
            for i in range(len(first) - length + 1)
            if all(first[i:i + length] in s for s in strings[1:])}


@settings(deadline=None)
@given(hs.lists(hs.text(alphabet="abc", min_size=1, max_size=12),
                min_size=2, max_size=4))
def test_hyp_lcs_lcsm_match_bruteforce(strings):
    st = STree.STree(strings)
    best = max((n for n in range(min(map(len, strings)), 0, -1)
                if brute_common_substrings(strings, n)), default=0)
    lcs = st.lcs()
    assert len(lcs) == best
    assert all(lcs in s for s in strings)
    if best == 0:
        assert st.lcsm() == []
    else:
        assert st.lcsm() == sorted(brute_common_substrings(strings, best))
