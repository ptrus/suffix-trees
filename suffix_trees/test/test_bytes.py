from suffix_trees import STree


def test_bytes_find():
    st = STree.STree(b"abcdefghab")
    assert st.find(b"abc") == 0
    assert st.find(b"xyz") == -1
    assert st.find_all(b"ab") == {0, 8}
    assert st.find_all(b"xyz") == set()


def test_bytes_non_ascii():
    data = bytes(range(256))
    st = STree.STree(data)
    assert st.find(bytes([250, 251, 252])) == 250
    assert st.find(bytes([251, 250])) == -1


def test_bytes_lcs():
    a = [b"xxxabcxxx", b"adsaabc", b"ytysabcrew", b"qqqabcqw", b"aaabc"]
    st = STree.STree(a)
    assert st.lcs() == b"abc"


def test_bytes_lcsm():
    a = [b"klexxxabc", b"kleyyyabc"]
    st = STree.STree(a)
    assert st.lcsm() == [b"abc", b"kle"]


def test_bytes_lcs_non_ascii():
    a = [bytes([0, 1, 2, 200, 201, 202]), bytes([5, 6, 200, 201, 202, 7])]
    st = STree.STree(a)
    assert st.lcs() == bytes([200, 201, 202])
