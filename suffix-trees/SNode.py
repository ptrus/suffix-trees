class SNode():
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
