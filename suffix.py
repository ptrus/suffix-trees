from collections import defaultdict


class STrie():
    def __init__(self, alphabet=''):
        self.aphabet = alphabet
        self.root = SNode()
        self.root.depth = 0
        self.root.idx = 0
        self.root.parent = self.root
        self.root.add_suffix_link(self.root)

    def build(self, x):
        self._build_naive(x)

    def _build_naive(self, x):
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
                u = self._createNode(x,u, d)
            self._createLeaf(x, i,u, d)
            u = self.root
            d = 0

    def _build_McCreight(self, x):
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
                u = self._createNode(x, u, d)
            self._createLeaf(x, i, u, d)
            if not u.get_suffix_link():
                self._computeSlink(x, u)
            u = u.get_suffix_link()
            d = d - 1
            if d < 0:
                d = 0

    def _createNode(self, x, u, d):
        i = u.idx
        p = u.parent
        v = SNode(idx=i, depth=d)
        v.add_transition_link(u,x[i+d])
        u.parent = v
        p.add_transition_link(v, x[i+p.depth])
        v.parent = p
        return v

    def _createLeaf(self, x, i, u, d):
        w = SNode()
        w.idx = i
        w.depth = len(x) - i
        u.add_transition_link(w, x[i + d])
        w.parent = u
        return w

    def _computeSlink(self, x, u):
        d = u.depth
        v = u.parent.get_suffix_link()
        while v.depth < d - 1:
            v = v.get_transition_link(x[u.idx + v.depth + 1])
        if v.depth > d - 1:
            v = self._createNode(x, v, d-1)
        u.add_suffix_link(v)


    def _build_Ukkonen(self, x):
        # TODO
        raise NotImplementedError()

    def build_generalized(self, xs):
        terminal_gen = self._terminal()
        _xs = ''.join([x + next(terminal_gen) for x in xs])
        self.build(_xs)
        #self.root._traverse(self._fix_generalized)

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
        for i in range(len(y)):
            currChar = y[i]
            node = node.get_transition_link(currChar)
            if not node:
                return -1
        return [node.idx,node.depth]

    def _terminal(self):
        # UTF PUA: U+E000..U+F8FF
        for i in range(0xE000,0xF8FF+1):
            yield(chr(i))

class SNode():
    def __init__(self, idx=-1, parentNode=None, depth=-1):
        # Links
        self._suffix_link = None
        self.transition_links = []
        # Properties
        self.substr = ""
        self.idx = idx
        self.depth = depth
        self.parent = parentNode

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

    def _traverse(self, f):
        for (node,_) in self.transition_links:
            self._traverse(node)
        f(self)
