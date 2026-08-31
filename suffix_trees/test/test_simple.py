from suffix_trees import STree


def test_lcs():
    a = ["abeceda", "abecednik", "abeabecedabeabeced",
         "abecedaaaa", "aaabbbeeecceeeddaaaaabeceda"]
    st = STree.STree(a)
    assert st.lcs() == "abeced", "LCS test"


def test_lcsm_single_result():
    a = ["abeceda", "abecednik", "abeabecedabeabeced",
         "abecedaaaa", "aaabbbeeecceeeddaaaaabeceda"]
    st = STree.STree(a)
    assert st.lcsm() == ["abeced"]


def test_lcsm_multiple_results():
    a = ["klexxxabc", "kleyyyabc"]
    st = STree.STree(a)
    assert st.lcsm() == ["abc", "kle"]


def test_lcsm_no_common_substring():
    a = ["abc", "def"]
    st = STree.STree(a)
    assert st.lcsm() == []


def test_lcsm_string_idxs():
    a = ["klexxxabc", "kleyyyabc", "zzzzzzzzz"]
    st = STree.STree(a)
    assert st.lcsm([0, 1]) == ["abc", "kle"]


def test_missing():
    text = "name language w en url http w namelanguage en url http"
    stree = STree.STree(text)
    assert stree.find("law") == -1
    assert stree.find("ptth") == -1
    assert stree.find("name language w en url http w namelanguage en url httpp") == -1


def test_find():
    st = STree.STree("abcdefghab")
    assert st.find("abc") == 0
    assert st.find_all("ab") == {0, 8}
