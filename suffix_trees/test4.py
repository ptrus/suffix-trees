import STree

if __name__ == '__main__':
    st = STree.STree('abcabxabcd')
    print st.suffix_array # [0, 6, 3, 1, 7, 4, 2, 8, 9, 5, 10]
    print st.bwt          # [u'\ue000', u'x', u'c', u'a', u'a', u'a', u'b', u'b', u'c', u'b', u'd']
    print st.lrs          # abc
    print st.bwt_entropy  # 0.864525000393
    print STree.STree('ABABABA').lrs          # ABABA
    print STree.STree('banana').suffix_array  # [1, 3, 5, 0, 2, 4, 6]
    print st.lcp_array                        # [3, 2, 0, 2, 1, 0, 1, 0, 0, 0]
    print STree.STree('banana').lcp_array     # [3, 1, 0, 0, 2, 0]
    st2 = STree.STree(['sandollar', 'sandlot', 'handler', 'grand', 'pantry'])
    for i in range(2,6):
        print i, st2.get_fcs_l(i)
    """ For frequent common string:
    i    l(i)   substrings

    2     4     ['andl', 'sand']
    3     3     ['and']
    4     3     ['and']
    5     2     ['an']
    """

