import sys, math
from os.path import commonprefix
from itertools import izip


class STree():
    """Class representing the suffix tree."""
    def __init__(self, input_string=None):
        self.root = _SNode()
        self.root.depth = 0
        self.root.idx = 0
        self.root.parent = self.root
        self.root._add_suffix_link(self.root)
        self._bwt = None
        self._bwt_entropy = None
        self._suffix_array = None
        self._lcp_array = None
        self._lrs = None
        self._fcs_l = None
        self._V = None
        self._Vs = None

        if input_string is not None:
            self.build(input_string)

    @staticmethod
    def _check_input(input_string):
        """Checks the validity of the input.

        In case of an invalid input throws ValueError.
        """
        if isinstance(input_string, str) or isinstance(input_string, unicode):
            return 'st'
        elif isinstance(input_string, list):
            if all(isinstance(i, str) for i in input_string) or \
                    all(isinstance(i, unicode) for i in input_string):
                return 'gst'

        raise ValueError("String argument should be of type String or"
                                     " a list of strings")

    def build(self, x):
        """Builds the Suffix tree on the given input.
        If the input is of type List of Strings:
        Generalized Suffix Tree is built.

        :param x: String or List of Strings
        """
        type = self._check_input(x)

        if type == 'st':
            x += next(self._terminalSymbolsGenerator())
            self._build(x)
        if type == 'gst':
            self._build_generalized(x)

    def _build(self, x):
        """Builds a Suffix tree."""
        self.word = x
        self._build_McCreight(x)

    def _build_McCreight(self, x):
        """Builds a Suffix tree using McCreight O(n) algorithm.

        Algorithm based on:
        McCreight, Edward M. "A space-economical suffix tree construction algorithm." - ACM, 1976.
        Implementation based on:
        UH CS - 58093 String Processing Algorithms Lecture Notes
        """
        u = self.root
        d = 0
        for i in range(len(x)):
            while u.depth == d and u._has_transition(x[d+i]):
                u = u._get_transition_link(x[d+i])
                d = d + 1
                while d < u.depth and x[u.idx + d] == x[i + d]:
                    d = d + 1
            if d < u.depth:
                u = self._create_node(x, u, d)
            self._create_leaf(x, i, u, d)
            if not u._get_suffix_link():
                self._compute_slink(x, u)
            u = u._get_suffix_link()
            d = d - 1
            if d < 0:
                d = 0

    def _create_node(self, x, u, d):
        i = u.idx
        p = u.parent
        v = _SNode(idx=i, depth=d)
        v._add_transition_link(u,x[i+d])
        u.parent = v
        p._add_transition_link(v, x[i+p.depth])
        v.parent = p
        return v

    def _create_leaf(self, x, i, u, d):
        w = _SNode()
        w.idx = i
        w.depth = len(x) - i
        u._add_transition_link(w, x[i + d])
        w.parent = u
        return w

    def _compute_slink(self, x, u):
        d = u.depth
        v = u.parent._get_suffix_link()
        while v.depth < d - 1:
            v = v._get_transition_link(x[u.idx + v.depth + 1])
        if v.depth > d - 1:
            v = self._create_node(x, v, d-1)
        u._add_suffix_link(v)


    def _build_Ukkonen(self, x):
        """Builds a Suffix tree using Ukkonen's online O(n) algorithm.

        Algorithm based on:
        Ukkonen, Esko. "On-line construction of suffix trees." - Algorithmica, 1995.
        """
        # TODO.
        raise NotImplementedError()

    def _build_generalized(self, xs):
        """Builds a Generalized Suffix Tree (GST) from the array of strings provided.
        """
        terminal_gen = self._terminalSymbolsGenerator()

        _xs = u''.join([x + next(terminal_gen) for x in xs])
        self.word = _xs
        self._generalized_word_starts(xs)
        self._build(_xs)
        self.root.traverse(self._label_generalized)

    def _label_generalized(self, node):
        """Helper method that labels the nodes of GST with indexes of strings
        found in their descendants.
        """
        if node.is_leaf():
            x = {self._get_word_start_index(node.idx)}
        else:
            x = {n for ns in node.transition_links for n in ns[0].generalized_idxs}
        node.generalized_idxs = x

    @property
    def suffix_array(self):
        """
        Computes the equivalent suffix array.

        :return:
        """
        if self._suffix_array is None:
            self._suffix_array = []
            self.root.lexicographical_traverse(self._get_suffix_array)
        return self._suffix_array

    def _get_suffix_array(self, node):
        if node.is_leaf():
            self.suffix_array.append(node.idx)

    def _get_word_start_index(self, idx):
        """Helper method that returns the index of the string based on node's
        starting index"""
        i = 0
        for _idx in self.word_starts[1:]:
            if idx < _idx:
                return i
            else:
                i+=1
        return i

    @property
    def bwt(self):
        """
        Burrows-Wheeler Transform.
        Please refer to:
        Burrows, M., & Wheeler, D. (1994). A block-sorting lossless data compression algorithm.
        Algorithm, Data Compression, (124), 18. https://doi.org/10.1.1.37.6774
        :return:
        """
        # TODO: implement bwt_inverse()
        if self._bwt is None:
            self._bwt = []
            self.root.lexicographical_traverse(self._get_bwt)
        return self._bwt

    def _get_bwt(self, node):
        if node.is_leaf():
            self._bwt.append(self.word[node.idx - 1])

    def lcs(self, stringIdxs=-1):
        """Returns the Largest Common Substring of Strings provided in stringIdxs.
        If stringIdxs is not provided, the LCS of all strings is returned.

        ::param stringIdxs: Optional: List of indexes of strings.
        """
        if stringIdxs == -1 or not isinstance(stringIdxs, list):
            stringIdxs = set(range(len(self.word_starts)))
        else:
            stringIdxs = set(stringIdxs)

        deepestNode = self._find_lcs(self.root, stringIdxs)
        start = deepestNode.idx
        end = deepestNode.idx + deepestNode.depth
        return self.word[start:end]

    def _find_lcs(self, node, stringIdxs):
        """Helper method that finds LCS by traversing the labeled GSD."""
        nodes = [self._find_lcs(n, stringIdxs)
            for (n,_) in node.transition_links
            if n.generalized_idxs.issuperset(stringIdxs)]

        if nodes == []:
            return node

        deepestNode = max(nodes, key=lambda n: n.depth)
        return deepestNode

    def _generalized_word_starts(self, xs):
        """Helper method returns the starting indexes of strings in GST"""
        self.word_starts = []
        i = 0
        for n in range(len(xs)):
            self.word_starts.append(i)
            i += len(xs[n]) + 1

    def find(self, y):
        """Returns starting position of the substring y in the string used for
        building the Suffix tree.

        :param y: String
        :return: Index of the starting position of string y in the string used for building the Suffix tree
                 -1 if y is not a substring.
        """
        node = self.root
        while True:
            edge = self._edgeLabel(node, node.parent)
            if edge.startswith(y):
                return node.idx
            
            i = 0
            while(i < len(edge) and edge[i] == y[0]):
                y = y[1:]
                i += 1
            
            if i != 0:
                if i == len(edge) and y != '':
                    pass
                else:
                    return -1
            
            node = node._get_transition_link(y[0])
            if not node:
                return -1

    def find_all(self, y):
        node = self.root
        while True:
            edge = self._edgeLabel(node, node.parent)
            if edge.startswith(y):
                break

            i = 0
            while(i < len(edge) and edge[i] == y[0]):
                y = y[1:]
                i += 1
            
            if i != 0:
                if i == len(edge) and y != '':
                    pass
                else:
                    return []

            node = node._get_transition_link(y[0])
            if not node:
                return []

        leaves = node._get_leaves()
        return [n.idx for n in leaves]

    @property
    def lrs(self):
        """
        Finds the longest repeated string, pretty similar to lcs().

        :return: longest repeated string
        """
        if self._lrs is None:
            deepest_leaf = self._find_lrs()
            self._lrs = self._edgeLabel(deepest_leaf.parent, self.root)
        return self._lrs

    def _find_lrs(self):
        leaf_nodes = self.root._get_leaves()
        deepest_leaf = max(leaf_nodes, key=lambda l: l.depth)
        return deepest_leaf

    @property
    def lcp_array(self):
        """
        Longest Common Prefix array (LCP).

        :return:
        """
        if self._lcp_array is None:
            self._lcp_array = self._get_lcp_array()
        return self._lcp_array

    def _get_lcp_array(self):
        return [len(commonprefix([self.word[i:],
                                  self.word[j:]])) for (i, j) in izip(self.suffix_array,
                                                                      self.suffix_array[1:])]

    def lps(self):
        """
        Find the longest palindrome sequence.
        Examples:
            banana -> anana
            pqrqpabcdfgdcba -> pqrqp

        :return:
        """
        # TODO
        raise NotImplementedError()

    def get_fcs_l(self, i):
        """
        Frequent Common String: For a set of string S = {S1,S2,...,Sk}, define l(i) for each
        i=2,3,...,k as the length of a maximal substring that is common to at least i strings of S.

        :return:
        """
        assert hasattr(self, 'word_starts')
        if i < 2:
            print "i has to be >= 2"
            return

        if self._fcs_l is None:
            self._V = [0] * (len(self.word_starts) + 1)
            self._Vs = [''] * (len(self.word_starts) + 1)
            self._compute_fcs()
        return self._fcs_l[i], self._Vs[i]

    def _compute_fcs(self):
        """ Where we actually compute fcs V and l vectors.
        """
        self.root.traverse(self._compute_V)
        self._fcs_l = [0] * (len(self.word_starts) + 1)
        self._fcs_l[-1] = self._V[-1]
        for i in range(2,len(self._fcs_l)-1)[::-1]:
            if self._fcs_l[i+1] > self._V[i]:
                self._Vs[i] = self._Vs[i+1][:]
            self._fcs_l[i] = max(self._fcs_l[i+1], self._V[i])

    def _compute_V(self, node):
        """
        """
        if not node.is_leaf():
            i = len(node.generalized_idxs)
            if node.depth == self._V[i]:
                self._Vs[i].append(self.word[node.idx:node.idx + node.depth])
            elif node.depth > self._V[i]:
                self._V[i] = node.depth
                self._Vs[i] = [self.word[node.idx:node.idx + node.depth]]

    @property
    def bwt_entropy(self):
        """Apply BWT then calculate the entropy for the input sequence. Ref:
        Cai, H., et al. (2004). Universal entropy estimation via block sorting.
        IEEE Transactions on Information Theory. Springer-Verlag Univ. Illinois Press.
        https://doi.org/10.1109/TIT.2004.830771
        """
        if self._bwt_entropy is None:
            self._bwt_entropy = _Entropy(self.bwt).bwt_entropy
        return self._bwt_entropy

    def _edgeLabel(self, node, parent):
        """Helper method, returns the edge label between a node and it's parent"""
        return self.word[node.idx + parent.depth : node.idx + node.depth]

    def _terminalSymbolsGenerator(self):
        """Generator of unique terminal symbols used for building the Generalized Suffix Tree.
        Unicode Private Use Area U+E000..U+F8FF is used to ensure that terminal symbols
        are not part of the input string.
        """
        py2 = sys.version[0] < '3'
        UPPAs = list(list(range(0xE000,0xF8FF+1)) + list(range(0xF0000,0xFFFFD+1)) + list(range(0x100000, 0x10FFFD+1)))
        for i in UPPAs:
            if py2:
                yield(unichr(i))
            else:
                yield(chr(i))
        raise ValueError("To many input strings.")


class _Entropy:
    """Class to compute different values of entropy from a suffix tree."""
    def __init__(self, z):
        """Calculate the BWT entropy for the input sequence z

        [1] Cai, H., et al. (2004). Universal entropy estimation via block sorting.
        IEEE Transactions on Information Theory. Springer-Verlag Univ. Illinois Press.
        https://doi.org/10.1109/TIT.2004.830771
        """
        self.bwt_entropy = _Entropy._bwt_entropy(z)

    @staticmethod
    def chunk_string(input_string, length):
        """ Code taken from SO:
        https://stackoverflow.com/questions/18854620
        """
        return (input_string[0 + i:length + i] for i in range(0, len(input_string), length))

    @staticmethod
    def _q_caret(a, j):
        """ From [1]:
        q(a,j) = N_j(a) / sum_{b in alphabet} N_j(b)

        That's basically the probability of 'a' in segment 'j'
        """
        return j.count(a) / float(len(j))

    @staticmethod
    def _log_q_caret(j):
        """ From [1]:
        log2 q(j) = sum_{a in alphabet} N_j(a) log2 q(a,j)

        That's the sum of occurences of every 'a' in 'j' times
        the probability of that 'a' appearing in every segment.
        We can simplify a bit: we can skip iterations when a given 'a'
        from the alphabet is not in 'j'
        """
        return math.fsum(j.count(a) * math.log(_Entropy._q_caret(a, j), 2.) for a in set(j))

    @staticmethod
    def _bwt_entropy(z):
        """
        Calculates the bwt_entropy [1] for an input sequence z. Note that z
        has to be a bwt from an input string (already implemented in the suffix tree class).
        :param z: input string, result of a BWT
        :return: value of the calculated bwt_entropy
        """
        # Calculate the size of the segments with which we'll split the sequence z [w(n)]
        # According to [1], the best (for a simple implementation) is sqrt(n), where n
        # is the length of z.
        w = int(round(math.sqrt(len(z))))

        # Perform the entropy calculation
        h_z = -1. / len(z) * math.fsum(_Entropy._log_q_caret(j) for j in _Entropy.chunk_string(z, w))

        return h_z


class _SNode:
    """Class representing a Node in the Suffix tree."""
    def __init__(self, idx=-1, parentNode=None, depth=-1):
        # Links
        self._suffix_link = None
        self.transition_links = []
        # Properties
        self.idx = idx
        self.depth = depth
        self.parent = parentNode
        self.generalized_idxs = {}

    def __str__(self):
        return("SNode: idx:"+ str(self.idx) + " depth:"+str(self.depth) +
            " transitons:" + str(self.transition_links))

    def _add_suffix_link(self, snode):
        self._suffix_link = snode

    def _get_suffix_link(self):
        if self._suffix_link != None:
            return self._suffix_link
        else:
            return False

    def _get_transition_link(self, suffix):
        for node,_suffix in self.transition_links:
            if _suffix == '__@__' or suffix == _suffix:
                return node
        return False

    def _add_transition_link(self, snode, suffix=''):
        tl = self._get_transition_link(suffix)
        if tl: # TODO: imporve this.
            self.transition_links.remove((tl,suffix))
        self.transition_links.append((snode,suffix))

    def _has_transition(self, suffix):
        for node,_suffix in self.transition_links:
            if _suffix == '__@__' or suffix == _suffix:
                return True
        return False

    def is_leaf(self):
        return self.transition_links == []

    def traverse(self, f):
        for (node,_) in self.transition_links:
            node.traverse(f)
        f(self)

    def lexicographical_traverse(self, f):
        """
        Same as _traverse() but lexicographically ordered. This is useful for
        building suffix arrays and Burrows-Wheeler Transform (BWT).

        :param f: function to be called at every node
        """
        for (node,_) in sorted(self.transition_links, key=lambda t: t[1]):
            node.lexicographical_traverse(f)
        f(self)

    def _get_leaves(self):
        if self.is_leaf():
            return [self]
        else:
            return [x for (n,_) in self.transition_links for x in n._get_leaves()]

