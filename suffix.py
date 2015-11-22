from collections import defaultdict


'''
TODO:
    - find/contains methods
    - check for any other basic
    - GST
'''
class STrie():
    def __init__(self):
        self.root = SNode()
        self.root.depth = 0
        self.root.idx = 0
        self.root.parent = self.root
        self.root.add_suffix_link(self.root)

    def build(self, x):
        self.word = x
        self.__build_McCreight__(x)

    def __build_naive__(self, x):
        self.__init__()
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
        self.__init__()
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
        # TODO
        raise NotImplementedError()

    def build_generalized(self, xs):
        terminal_gen = self.__terminalSymbols__()

        _xs = ''.join([x + next(terminal_gen) for x in xs])

        self.__generalized_word_starts(xs)

        self.build(_xs)
        self.root.__traverse__(self.__label_generalized)

    def __label_generalized(self, node):
        if node.is_Leaf():
            x = {self.__get_word_start_index(node.idx)}
        else:
            x = {n for ns in node.transition_links for n in ns[0].generalized_idxs}
        node.generalized_idxs = x

    def __get_word_start_index(self, idx):
        i = 0
        for _idx in self.word_starts[1:]:
            if idx < _idx:
                return i
            else:
                i+=1
        return i
        #raise Exception("Word start idx exceed max word start.")

    def LCS(self, stringIdxs=-1):
        if stringIdxs == -1 or not isinstance(stringIdxs, list):
            stringIdxs = set(range(len(self.word_starts)))
        else:
            stringIdxs = set(stringIdxs)

        deepestNode = self.__find_lcs__(self.root, stringIdxs)
        start = deepestNode.idx
        end = deepestNode.idx + deepestNode.depth
        return self.word[start:end]

    def __find_lcs__(self, node, stringIdxs):
        nodes = [self.__find_lcs__(n, stringIdxs)
            for (n,_) in node.transition_links
            if n.generalized_idxs.issuperset(stringIdxs)]

        if nodes == []:
            return node

        deepestNode = max(nodes, key=lambda n: n.depth)
        return deepestNode

    def __generalized_word_starts(self, xs):
        self.word_starts = []
        i = 0
        for n in range(len(xs)):
            self.word_starts.append(i)
            i += len(xs[n]) + 1

    def contains(self, y):
        node = self.root
        for i in range(len(y)):
            currChar = y[i]
            node = node.get_transition_link(currChar)
            if not node:
                return False
        return True

    def find(self, y):
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

    def __edgeLabel__(self, node, parent):
        return self.word[node.idx + parent.depth : node.idx + node.depth]


    def __terminalSymbols__(self):
        # UTF PUA: U+E000..U+F8FF
        for i in range(0xE000,0xF8FF+1):
            yield(chr(i))

class SNode():
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

    def add_suffix_link(self, snode):
        self._suffix_link = snode

    def get_suffix_link(self):
        if self._suffix_link != None:
            return self._suffix_link
        else:
            return False

    def get_transition_link(self, suffix):
        for node,_suffix in self.transition_links:
            if _suffix == '__@__' or suffix == _suffix:
                return node
        return False

    def add_transition_link(self, snode, suffix=''):
        tl = self.get_transition_link(suffix)
        if tl: # TODO: imporve this.
            self.transition_links.remove((tl,suffix))
        self.transition_links.append((snode,suffix))

    def has_transition(self, suffix):
        for node,_suffix in self.transition_links:
            if _suffix == '__@__' or suffix == _suffix:
                return True
        return False

    def is_Leaf(self):
        return self.transition_links == []

    def __traverse__(self, f):
        for (node,_) in self.transition_links:
            node.__traverse__(f)
        f(self)
