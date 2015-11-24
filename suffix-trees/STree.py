class STree():
    """Class representing the suffix tree."""
    def __init__(self, input=''):
        self.root = SNode()
        self.root.depth = 0
        self.root.idx = 0
        self.root.parent = self.root
        self.root.add_suffix_link(self.root)

        if not input == '':
           self.build(input)

    def __check_input__(self, input):
        """Checks the validity of the input.

        In case of an invalid input throws ValueError.
        """
        if isinstance(input, str):
            return 'st'
        elif isinstance(input, list):
            if all(isinstance(item, str) for item in input):
                return 'gst'

        raise ValueError("String argument should be of type String or"
                                     " a list of strings")

    def build(self, x):
        """Builds the Suffix tree on the given input.
        If the input is of type List of Strings:
        Generalized Suffix Tree is built.

        :param x: String or List of Strings
        """
        type = self.__check_input__(x)

        if type == 'st':
            x += next(self.__terminalSymbolsGenerator__())
            self.__build__(x)
        if type == 'gst':
            self.__build_generalized__(x)

    def __build__(self, x):
        """Builds the Suffix tree."""
        self.word = x
        self.__build_McCreight__(x)

    def __build_naive__(self, x):
        """Builds a Suffix tree using the naive O(n^2) algorithm."""
        u = self.root
        d = 0
        for i in range(len(x)):
            while d == u.depth and u.has_transition(x[i+d]):
                u = u.get_transition_link(x[i+d])
                d += 1
                while d < u.depth and x[u.idx + d] == x[i+d]:
                    d += 1
            if d < u.depth:
                u = self.__createNode__(x,u, d)
            self.__createLeaf__(x, i,u, d)
            u = self.root
            d = 0

    def __build_McCreight__(self, x):
        """Builds a Suffix tree using McCreight O(n) algorithm.

        Algorithm based on:
        McCreight, Edward M. "A space-economical suffix tree construction algorithm." - ACM, 1976.
        """
        u = self.root
        d = 0
        for i in range(len(x)):
            while u.depth == d and u.has_transition(x[d+i]):
                u = u.get_transition_link(x[d+i])
                d = d + 1
                while d < u.depth and x[u.idx + d] == x[i + d]:
                    d = d + 1
            if d < u.depth:
                u = self.__createNode__(x, u, d)
            self.__createLeaf__(x, i, u, d)
            if not u.get_suffix_link():
                self.__computeSlink__(x, u)
            u = u.get_suffix_link()
            d = d - 1
            if d < 0:
                d = 0

    def __createNode__(self, x, u, d):
        i = u.idx
        p = u.parent
        v = SNode(idx=i, depth=d)
        v.add_transition_link(u,x[i+d])
        u.parent = v
        p.add_transition_link(v, x[i+p.depth])
        v.parent = p
        return v

    def __createLeaf__(self, x, i, u, d):
        w = SNode()
        w.idx = i
        w.depth = len(x) - i
        u.add_transition_link(w, x[i + d])
        w.parent = u
        return w

    def __computeSlink__(self, x, u):
        d = u.depth
        v = u.parent.get_suffix_link()
        while v.depth < d - 1:
            v = v.get_transition_link(x[u.idx + v.depth + 1])
        if v.depth > d - 1:
            v = self.__createNode__(x, v, d-1)
        u.add_suffix_link(v)


    def __build_Ukkonen__(self, x):
        """Builds a Suffix tree using Ukkonen's online O(n) algorithm.

        Algorithm based on:
        Ukkonen, Esko. "On-line construction of suffix trees." - Algorithmica, 1995.
        """
        # TODO.
        raise NotImplementedError()

    def __build_generalized__(self, xs):
        '''Builds a Generalized Suffix Tree (GST) from the array of strings provided.
        '''
        terminal_gen = self.__terminalSymbolsGenerator__()

        _xs = ''.join([x + next(terminal_gen) for x in xs])
        self.word = _xs
        self.__generalized_word_starts__(xs)
        self.__build__(_xs)
        self.root.__traverse__(self.__label_generalized__)

    def __label_generalized__(self, node):
        '''Helper method that labels the nodes of GST with indexes of strings
        found in their descendants.
        '''
        if node.is_Leaf():
            x = {self.__get_word_start_index__(node.idx)}
        else:
            x = {n for ns in node.transition_links for n in ns[0].generalized_idxs}
        node.generalized_idxs = x

    def __get_word_start_index__(self, idx):
        '''Helper method that returns the index of the string based on node's
        starting index'''
        i = 0
        for _idx in self.word_starts[1:]:
            if idx < _idx:
                return i
            else:
                i+=1
        return i

    def LCS(self, stringIdxs=-1):
        '''Returns the Largest Common Substring of Strings provided in stringIdxs.
        If stringIdxs is not provided, the LCS of all strings is returned.

        ::param stringIdxs: Optional: List of indexes of strings.
        '''
        if stringIdxs == -1 or not isinstance(stringIdxs, list):
            stringIdxs = set(range(len(self.word_starts)))
        else:
            stringIdxs = set(stringIdxs)

        deepestNode = self.__find_lcs__(self.root, stringIdxs)
        start = deepestNode.idx
        end = deepestNode.idx + deepestNode.depth
        return self.word[start:end]

    def __find_lcs__(self, node, stringIdxs):
        '''Helper method that finds LCS by traversing the labeled GSD.'''
        nodes = [self.__find_lcs__(n, stringIdxs)
            for (n,_) in node.transition_links
            if n.generalized_idxs.issuperset(stringIdxs)]

        if nodes == []:
            return node

        deepestNode = max(nodes, key=lambda n: n.depth)
        return deepestNode

    def __generalized_word_starts__(self, xs):
        """Helper method returns the starting indexes of strings in GST"""
        self.word_starts = []
        i = 0
        for n in range(len(xs)):
            self.word_starts.append(i)
            i += len(xs[n]) + 1

    def find(self, y):
        """ Returns starting position of the substring y in the string used for
        building the Suffix tree.

        :param y: String
        :return: Index of the starting position of string y in the string used for building the Suffix tree
                 -1 if y is not a substring.
        """
        node = self.root
        while True:
            edge = self.__edgeLabel__(node, node.parent)
            if edge.startswith(y):
                return node.idx
            i = 0
            while(i < len(edge) and edge[i] == y[0]):
                y = y[1:]
                i += 1
            node = node.get_transition_link(y[0])
            if not node:
                return -1

    def find_all(self, y):
        idxs = []
        y_input = y
        node = self.root
        while True:
            edge = self.__edgeLabel__(node, node.parent)
            if edge.startswith(y):
                idxs.append(node.idx)
                break
            else:
                i = 0
                while(i < len(edge) and edge[i] == y[0]):
                    y = y[1:]
                    i += 1
            node = node.get_transition_link(y[0])
            if not node:
                return idxs
        leaves = self.__find_leaves__(node, [])
        return [n.idx for n in leaves]

    def __find_leaves__(self, node, leaves=[]):
        if node.is_Leaf():
            leaves.append(node)
        else:
            for (n,_) in node.transition_links:
                leaves = leaves + self.__find_leaves__(n, [])
        return leaves

    def __edgeLabel__(self, node, parent):
        """Helper method, returns the edge label between a node and it's parent"""
        return self.word[node.idx + parent.depth : node.idx + node.depth]


    def __terminalSymbolsGenerator__(self):
        """Generator of unique terminal symbols used for building the Generalized Suffix Tree.
        Unicode Private Use Area U+E000..U+F8FF is used to ensure that terminal symbols
        are not part of the input string.
        """
        for i in range(0xE000,0xF8FF+1):
            yield(chr(i))
        raise ValueError("To many input strings.")