from __future__ import annotations

from collections.abc import Generator, Iterable
from typing import Callable


class STree:
    """Class representing the suffix tree."""

    BUILDERS = ('mccreight', 'ukkonen')

    def __init__(self, data: str | bytes | list[str] | list[bytes] | None = None,
                 builder: str = 'mccreight'):
        if builder not in self.BUILDERS:
            raise ValueError(f"Unknown builder {builder!r}, expected one of {self.BUILDERS}")
        self.builder = builder
        self.root = _SNode()
        self.root.depth = 0
        self.root.idx = 0
        self.root.parent = self.root
        self.root._add_suffix_link(self.root)
        self.word = ""
        self.word_starts: list[int] = []
        self._bytes_input = False

        if data:
            self.build(data)

    def _check_input(self, data: str | bytes | list[str] | list[bytes]) -> str:
        """Checks the validity of the input.

        In case of an invalid input throws ValueError.
        """
        if isinstance(data, (str, bytes)):
            return 'st'
        elif isinstance(data, list):
            if all(isinstance(item, str) for item in data):
                return 'gst'
            if all(isinstance(item, bytes) for item in data):
                return 'gst'

        raise ValueError("Argument should be str, bytes, a list of str or a list of bytes")

    def _decode(self, data: str | bytes) -> str:
        """Helper method that maps input to the internal string representation.

        Bytes are decoded via latin-1, which maps each byte 1:1 to U+0000..U+00FF.
        This preserves offsets, keeps every byte value distinct and never collides
        with the private-use-area terminal symbols.
        """
        if isinstance(data, bytes):
            self._bytes_input = True
            return data.decode('latin-1')
        return data

    def _encode(self, word: str) -> str | bytes:
        """Helper method that maps an internal string back to the input type."""
        if self._bytes_input:
            return word.encode('latin-1')
        return word

    def build(self, x: str | bytes | list[str] | list[bytes]) -> None:
        """Builds the Suffix tree on the given input.
        If the input is of type List of Strings:
        Generalized Suffix Tree is built.

        :param x: String or List of Strings (str or bytes)
        """
        tree_type = self._check_input(x)

        if tree_type == 'st':
            x = self._decode(x)
            x += next(self._terminalSymbolsGenerator())
            self._build(x)
        if tree_type == 'gst':
            x = [self._decode(item) for item in x]
            self._build_generalized(x)

    def _build(self, x: str) -> None:
        """Builds a Suffix tree."""
        self.word = x
        if self.builder == 'ukkonen':
            self._build_Ukkonen(x)
        else:
            self._build_McCreight(x)

    def _build_McCreight(self, x: str) -> None:
        """Builds a Suffix tree using McCreight O(n) algorithm.

        Algorithm based on:
        McCreight, Edward M. "A space-economical suffix tree construction algorithm." - ACM, 1976.
        Implementation based on:
        UH CS - 58093 String Processing Algorithms Lecture Notes
        """
        u = self.root
        d = 0
        for i in range(len(x)):
            while u.depth == d and u._has_transition(x[d + i]):
                u = u._get_transition_link(x[d + i])
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

    def _create_node(self, x: str, u: _SNode, d: int) -> _SNode:
        i = u.idx
        p = u.parent
        v = _SNode(idx=i, depth=d)
        v._add_transition_link(u, x[i + d])
        u.parent = v
        p._add_transition_link(v, x[i + p.depth])
        v.parent = p
        return v

    def _create_leaf(self, x: str, i: int, u: _SNode, d: int) -> _SNode:
        w = _SNode()
        w.idx = i
        w.depth = len(x) - i
        u._add_transition_link(w, x[i + d])
        w.parent = u
        return w

    def _compute_slink(self, x: str, u: _SNode) -> None:
        d = u.depth
        v = u.parent._get_suffix_link()
        while v.depth < d - 1:
            v = v._get_transition_link(x[u.idx + v.depth + 1])
        if v.depth > d - 1:
            v = self._create_node(x, v, d - 1)
        u._add_suffix_link(v)

    def _build_Ukkonen(self, x: str) -> None:
        """Builds a Suffix tree using Ukkonen's online O(n) algorithm.

        Algorithm based on:
        Ukkonen, Esko. "On-line construction of suffix trees." - Algorithmica, 1995.

        The active point is kept as (active_node, active_edge, active_length).
        Since the whole string is known up front, leaves are created with their
        final depth directly (the usual "open end" is always the end of x).
        """
        n = len(x)
        root = self.root
        active_node = root
        active_edge = 0    # position in x of the first character of the active edge
        active_length = 0
        remainder = 0      # suffixes still to be inserted in the current phase
        for i in range(n):
            remainder += 1
            last_internal = None
            while remainder > 0:
                if active_length == 0:
                    active_edge = i
                child = active_node._get_transition_link(x[active_edge])
                if child is None:
                    # Rule 2: no edge starts with x[i] here - add a leaf.
                    self._create_leaf(x, i - active_node.depth, active_node, active_node.depth)
                    if last_internal is not None:
                        last_internal._add_suffix_link(active_node)
                        last_internal = None
                else:
                    edge_length = child.depth - active_node.depth
                    if active_length >= edge_length:
                        # Walk down: the active point lies beyond this edge.
                        active_node = child
                        active_edge += edge_length
                        active_length -= edge_length
                        continue
                    if x[child.idx + active_node.depth + active_length] == x[i]:
                        # Rule 3: x[i] is already on the edge - phase ends.
                        if last_internal is not None and active_node is not root:
                            last_internal._add_suffix_link(active_node)
                        active_length += 1
                        break
                    # Rule 2: split the edge and add a leaf.
                    split = self._create_node(x, child, active_node.depth + active_length)
                    self._create_leaf(x, i - split.depth, split, split.depth)
                    if last_internal is not None:
                        last_internal._add_suffix_link(split)
                    last_internal = split

                remainder -= 1
                if active_node is root and active_length > 0:
                    active_length -= 1
                    active_edge = i - remainder + 1
                elif active_node is not root:
                    slink = active_node._get_suffix_link()
                    active_node = slink if slink is not None else root

    def _build_generalized(self, xs: list[str]) -> None:
        """Builds a Generalized Suffix Tree (GST) from the array of strings provided.
        """
        terminal_gen = self._terminalSymbolsGenerator()

        _xs = ''.join([x + next(terminal_gen) for x in xs])
        self.word = _xs
        self._generalized_word_starts(xs)
        self._build(_xs)
        self.root._traverse(self._label_generalized)

    def _label_generalized(self, node: _SNode) -> None:
        """Helper method that labels the nodes of GST with indexes of strings
        found in their descendants.
        """
        if node.is_leaf():
            x = {self._get_word_start_index(node.idx)}
        else:
            x = {n for ns in node.transition_links.values() for n in ns.generalized_idxs}
        node.generalized_idxs = x

    def _get_word_start_index(self, idx: int) -> int:
        """Helper method that returns the index of the string based on node's
        starting index"""
        i = 0
        for _idx in self.word_starts[1:]:
            if idx < _idx:
                return i
            else:
                i += 1
        return i

    def lcs(self, stringIdxs: int | list[int] = -1) -> str | bytes:
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
        return self._encode(self.word[start:end])

    def _find_lcs(self, node: _SNode, stringIdxs: set[int]) -> _SNode:
        """Helper method that finds LCS by traversing the labeled GSD."""
        nodes = [self._find_lcs(n, stringIdxs)
                 for n in node.transition_links.values()
                 if n.generalized_idxs.issuperset(stringIdxs)]

        if nodes == []:
            return node

        deepestNode = max(nodes, key=lambda n: n.depth)
        return deepestNode

    def lcsm(self, stringIdxs: int | list[int] = -1) -> list[str] | list[bytes]:
        """Returns all Largest Common Substrings of Strings provided in stringIdxs.
        Like lcs(), but returns a sorted list of all common substrings of maximal
        length instead of an arbitrary one of them.
        If stringIdxs is not provided, the LCSs of all strings are returned.

        ::param stringIdxs: Optional: List of indexes of strings.
        """
        if stringIdxs == -1 or not isinstance(stringIdxs, list):
            stringIdxs = set(range(len(self.word_starts)))
        else:
            stringIdxs = set(stringIdxs)

        deepestNodes: list[_SNode] = []
        self._find_lcsm(self.root, stringIdxs, deepestNodes)
        if not deepestNodes:
            return []

        maxDepth = max(n.depth for n in deepestNodes)
        if maxDepth == 0:
            return []

        return sorted(self._encode(self.word[n.idx:n.idx + n.depth])
                      for n in deepestNodes if n.depth == maxDepth)

    def _find_lcsm(self, node: _SNode, stringIdxs: set[int], out: list[_SNode]) -> None:
        """Helper method that collects all deepest nodes common to stringIdxs.

        Appends to out every node whose subtree contains suffixes of all the
        requested strings and that has no such descendant (i.e. is locally
        deepest). Every common substring of maximal length labels one of them.
        """
        children = [n for n in node.transition_links.values()
                    if n.generalized_idxs.issuperset(stringIdxs)]

        if not children:
            out.append(node)
            return

        for child in children:
            self._find_lcsm(child, stringIdxs, out)

    def _generalized_word_starts(self, xs: list[str]) -> None:
        """Helper method returns the starting indexes of strings in GST"""
        self.word_starts = []
        i = 0
        for n in range(len(xs)):
            self.word_starts.append(i)
            i += len(xs[n]) + 1

    def find(self, y: str | bytes) -> int:
        """Returns starting position of the substring y in the string used for
        building the Suffix tree.

        :param y: String (str or bytes)
        :return: Index of the starting position of string y in the string used for building the Suffix tree
                 -1 if y is not a substring.
        """
        if isinstance(y, bytes):
            y = y.decode('latin-1')
        node = self.root
        while True:
            edge = self._edgeLabel(node, node.parent)
            if edge.startswith(y):
                return node.idx

            i = 0
            while (i < len(edge) and edge[i] == y[0]):
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

    def find_all(self, y: str | bytes) -> set[int]:
        """Returns starting positions of all occurrences of the substring y
        in the string used for building the Suffix tree.

        :param y: String (str or bytes)
        :return: Set of starting positions of string y in the string used for building the Suffix tree.
                 Empty set if y is not a substring.
        """
        if isinstance(y, bytes):
            y = y.decode('latin-1')
        node = self.root
        while True:
            edge = self._edgeLabel(node, node.parent)
            if edge.startswith(y):
                break

            i = 0
            while (i < len(edge) and edge[i] == y[0]):
                y = y[1:]
                i += 1

            if i != 0:
                if i == len(edge) and y != '':
                    pass
                else:
                    return set()

            node = node._get_transition_link(y[0])
            if not node:
                return set()

        leaves = node._get_leaves()
        return {n.idx for n in leaves}

    def _edgeLabel(self, node: _SNode, parent: _SNode) -> str:
        """Helper method, returns the edge label between a node and it's parent"""
        return self.word[node.idx + parent.depth: node.idx + node.depth]

    def _terminalSymbolsGenerator(self) -> Generator[str, None, None]:
        """Generator of unique terminal symbols used for building the Generalized Suffix Tree.
        Unicode Private Use Area U+E000..U+F8FF is used to ensure that terminal symbols
        are not part of the input string.
        """
        UPPAs = list(list(range(0xE000, 0xF8FF + 1)) +
                     list(range(0xF0000, 0xFFFFD + 1)) + list(range(0x100000, 0x10FFFD + 1)))
        for i in UPPAs:
            yield (chr(i))

        raise ValueError("Too many input strings.")


class _SNode:
    __slots__ = ['_suffix_link', 'transition_links', 'idx', 'depth', 'parent', 'generalized_idxs']

    """Class representing a Node in the Suffix tree."""

    def __init__(self, idx: int = -1, parentNode: _SNode | None = None, depth: int = -1):
        # Links
        self._suffix_link: _SNode | None = None
        self.transition_links: dict[str, _SNode] = {}
        # Properties
        self.idx = idx
        self.depth = depth
        self.parent = parentNode
        self.generalized_idxs: set[int] = set()

    def __str__(self) -> str:
        return ("SNode: idx:" + str(self.idx) + " depth:" + str(self.depth) +
                " transitons:" + str(list(self.transition_links.keys())))

    def _add_suffix_link(self, snode: _SNode) -> None:
        self._suffix_link = snode

    def _get_suffix_link(self) -> _SNode | None:
        return self._suffix_link

    def _get_transition_link(self, suffix: str) -> _SNode | None:
        return self.transition_links.get(suffix)

    def _add_transition_link(self, snode: _SNode, suffix: str) -> None:
        self.transition_links[suffix] = snode

    def _has_transition(self, suffix: str) -> bool:
        return suffix in self.transition_links

    def is_leaf(self) -> bool:
        return len(self.transition_links) == 0

    def _traverse(self, f: Callable[[_SNode], None]) -> None:
        for node in self.transition_links.values():
            node._traverse(f)
        f(self)

    def _get_leaves(self) -> Iterable[_SNode]:
        # Python <3.6 dicts don't perserve insertion order (and even after, we
        # shouldn't rely on dicts perserving the order) therefore these can be
        # out-of-order, so we return a set of leaves.
        if self.is_leaf():
            return {self}
        else:
            return {x for n in self.transition_links.values() for x in n._get_leaves()}
