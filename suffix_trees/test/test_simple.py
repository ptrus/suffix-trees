from suffix_trees import STree


def test_lcs():
    a = ["abeceda", "abecednik", "abeabecedabeabeced",
         "abecedaaaa", "aaabbbeeecceeeddaaaaabeceda"]
    st = STree.STree(a)
    assert st.lcs() == "abeced", "LCS test"


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
