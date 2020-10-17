# -*- coding: utf-8 -*-
"""
Created on Wed Aug 08 13:10:37 2012

@author: hlampesberger
"""

import collections
import pyparsing as pp

from base import state_generator

__all__ = ['Tree', 'Node']


class Node(object):
    def __init__(self, label, data=None):
        self.label = label
        self.data = data
        self.state = None
    def __repr__(self):
        return "<Node \"%s\" id:%d>" % (self.label, id(self))
    def __eq__(self, other):
        return self.label == other.label
    def __str__(self):
        return str(self.label)
    def __copy__(self):
        n = Node(self.label)
        n.data = self.data
        n.state = self.state
        return n
    def to_nw_call(self):
        return "<%s" % self.label
    def to_nw_return(self):
        return "%s>" % self.label
    def to_xml_open(self):
        return "<%s>" % self.label
    def to_xml_close(self):
        return "</%s>" % self.label
    copy = __copy__


# a finite tree
class Tree(object):
    def __init__(self, root_node, children=[], from_subtree_iter=None):
        if isinstance(root_node, Node):
            self.root = root_node
        else:
            self.root = Node(root_node)
        self._parent = {self.root : None}
        self._children = { self.root : [] }
        self._nodelevel = {self.root: 1}
        self._depth = {self.root : 1}
        for ch in children:
            self._parent.update(ch._parent)
            self._children.update(ch._children)
            self._depth.update(ch._depth)
            if ch._depth[ch.root] + 1 > self._depth[self.root]:
                self._depth[self.root] = ch._depth[ch.root] + 1
            self._nodelevel.update({n:c + 1 for n, c in ch._nodelevel.items()})
            self._parent[ch.root] = self.root
            self._children[self.root].append(ch.root)

        if from_subtree_iter is not None:
            for n, par in from_subtree_iter:
                if par is not None:
                    self._children[n] = []
                    self._children[par].append(n)
                    self._parent[n] = par
                    self._depth[n] = 0
                    self._nodelevel[n] = self._nodelevel[par] + 1
            # update depth
            stack = [self.root]
            while stack:
                top = stack[-1]
                if self.is_leaf(top):
                    self._depth[top] = 1
                    stack.pop()
                else:
                    zero_depth = [n for n in self._children[top] \
                                  if self._depth[n] == 0]
                    if zero_depth:
                        stack.extend(zero_depth)
                    else:
                        self._depth[top] = 1 + \
                                           self._depth[max(self._children[top],
                                           key=self._depth.get)]
                        stack.pop()


    def __contains__(self, node):
        return node in self._parent

    def __repr__(self):
        return "<Tree p:%d ch:%d>" % (len(self._parent), len(self._children))

    def __len__(self):
        return len(self._parent)

    def __iter__(self):
        return self.breadth_first_traverse()

    def __deepcopy__(self):
        # also copies nodes
        cp = Tree(self.root.copy())
        node_rel = { n : n.copy() for n in self._parent.keys() \
                     if id(n) != id(cp.root) }
        node_rel[self.root] = cp.root

        for node, parent in self._parent.items():
            if parent is not None:
                cp._parent[node_rel[node]] = node_rel[parent]

        for node, children in self._children.items():
            cp_children = [ node_rel[n] for n in children ]
            cp._children[node_rel[node]] = cp_children
        return cp

    def __copy__(self):
        # only duplicates edges
        tr = Tree(self.root)
        tr._parent = self._parent.copy()
        tr._children = self._children.copy()
        return tr

    def __eq__(self, other):
        queue = collections.deque([ (self.root, other.root) ])
        while queue:
            # print "queue length", len(queue)
            l, r = queue.popleft()
            if (l == r) and (self._parent[l] == other._parent[r]) and \
               (self.arity(l) == other.arity(r)):
                queue.extend(zip(self._children[l], other._children[r]))
            else:
                return False
        return True

    def __str__(self):
        return ''.join(self.fcns_decorate(lambda n: "%s(" % str(n),
                                          lambda n: ")"))

    def children(self, node):
        return self._children[node]

    def parent(self, node):
        return self._parent[node]

    def nodes(self):
        return self._parent.keys()

    def nodelevel(self, node):
        return self._nodelevel[node]

    def level(self, k, node=None):
        if node is None:
            node = self.root
        queue = collections.deque([(node, 1)])
        while queue:
            n, level = queue.popleft()
            if level < k:
                queue.extend((ch, level + 1) for ch in self.children(n))
            elif level == k:
                yield n
            else:
                break

    def to_xml(self):
        return ''.join(self.fcns_decorate(lambda n: n.to_xml_open(),
                                          lambda n: n.to_xml_close()))

    def to_word(self):
        return self.fcns_decorate(lambda n: n.to_nw_call(),
                                  lambda n: n.to_nw_return())


    def tagged_alphabet(self):
        return {(n.to_nw_call(), n.to_nw_return()) for n in self._parent.keys()}

    def fcns_decorate(self, call_decorator, return_decorator):
        # uses first child next sibling traversal and deco functions
        ch_idx = { n : 0 for n, ch in self._children.items() if ch }
        buf = [call_decorator(self.root)]
        node = self.root
        while node is not None:
            # print buf
            if self._children[node] and ch_idx[node] == 0:
                # print "fc"
                # goto first child
                ch_idx[node] += 1
                node = self._children[node][0]
                buf.append(call_decorator(node))
            elif self.is_root(node):
                # print "root return"
                buf.append(return_decorator(node))
                node = self._parent[node]
            elif ch_idx[self._parent[node]] < self.num_siblings(node):
                # print "ns"
                # goto next sibling
                buf.append(return_decorator(node))
                parent = self._parent[node]
                node = self._children[parent][ch_idx[parent]]
                ch_idx[parent] += 1
                buf.append(call_decorator(node))
            else:
                # print "ret"
                buf.append(return_decorator(node))
                node = self._parent[node]
        return buf

    def num_siblings(self, node):
        if self.is_root(node):
            return len(self._children[node])
        else:
            return len(self._children[self._parent[node]])

    def is_root(self, node):
        return id(self.root) == id(node)

    def is_leaf(self, node):
        return not self._children[node]

    def arity(self, node):
        return len(self._children[node])

    def leaves(self):
        return { n for n in self if not self._children[n] }

    def subtree(self, new_root, leaves=[]):
        # tr = Tree(new_root, children=self._children[new_root])
        leaves = set(leaves)
        def gen():
            queue = collections.deque([new_root])
            while queue:
                n = queue.popleft()
                if id(n) == id(new_root):
                    yield n, None
                else:
                    yield n, self._parent[n]
                if leaves:
                    if n not in leaves:
                        queue.extend(self._children[n])
                else:
                    queue.extend(self._children[n])
        return Tree(new_root, from_subtree_iter=gen())

    def path(self, node):
        path = collections.deque([node])
        node = self.parent(node)
        while node is not None:
            path.appendleft(node)
            node = self.parent(node)

    def k_root(self, k):
        assert(k > 0)
        return self.subtree(self.root, leaves=self.level(k))

    def k_fork(self, k):
        assert(k > 0)
        for node in [n for n, d in self._depth.items() if d >= k]:
            yield self.subtree(node, leaves=self.level(k, node))

    def k_subtree(self, k):
        assert(k > 0)
        planed = self.leaves()
        queue = collections.deque((n, 1) for n in planed)
        while queue:
            node, i = queue.popleft()
            if i <= k:
                yield self.subtree(node)
                par = self.parent(node)
                if par not in planed and par is not None:
                    planed.add(par)
                    queue.append((par, self.depth(par)))

    def breadth_first_traverse(self, root=None):
        if root is None:
            root = self.root
        queue = collections.deque([root])
        while queue:
            # print "queue length", len(queue)
            node = queue.popleft()
            yield node
            queue.extend(self._children[node])

    def depth_first_traverse(self, root=None):
        if root is None:
            root = self.root
        stack = [root]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(self._children[node]))

    def bottom_up_traverse(self):
        return sorted(self._depth, key=self._depth.get)

    def depth(self, node=None):
        if node is None:
            node = self.root
        return self._depth[node]

    def write_graphviz(self, path):
        with open(path, "w") as f:
            # header
            f.write("graph G {\n")
            f.write("  graph [ordering=\"out\"];\n")
            id_gen = state_generator()
            nodes_id = { n : next(id_gen) for n in self._parent.keys() }
            # content
            for node in self.breadth_first_traverse():
                nid = nodes_id[node]
                if node.state is not None:
                    f.write("  n%d [label=\"%s:%s\"];\n" % (nid, str(node),
                                                            node.state))
                else:
                    f.write("  n%d [label=\"%s\"];\n" % (nid, str(node)))
            for node in self.breadth_first_traverse():
                if not self.is_root(node):
                    f.write("  n%d -- n%d;\n" % (nodes_id[self._parent[node]],
                                                 nodes_id[node]))
            # trailer
            f.write("}\n")

    @classmethod
    def parse(cls, strng):
        label = pp.Word(pp.alphanums + "_")
        expr = pp.Forward().setParseAction(cls._pp_build_tree)
        expr << label + pp.nestedExpr('(', ')', content=expr)
        hedge = expr.parseString(strng)
        if len(hedge) > 1:
            raise RuntimeError("Too many roots for a tree!")
        return hedge[0]

    @classmethod
    def _pp_build_tree(cls, s, l, t):
        return Tree(Node(t[0]), children=t[1])

    copy = __copy__
    deepcopy = __deepcopy__
    to_string = __str__


