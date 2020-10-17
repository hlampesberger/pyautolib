# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 10:12:09 2012

@author: hlampesberger
"""


import unittest
import operator

from data.tree import Tree
from data.sparse_matrix import SparseStateMatrix
from base import Result

__all__ = ['DTA']

epsilon = ""


# deterministic bottom-up ranked tree automaton
class DTA(object):
    def __init__(self, ranked_alphabet, states, accept_states, delta):
        self.alphabet = ranked_alphabet
        self.states = states
        self.accept_states = accept_states
        self.delta = delta

    @staticmethod
    def build(**kwargs):
        alp = set(kwargs.get('alphabet'))
        states = set(kwargs.get('states'))
        acc = set(kwargs.get('accept_states'))
        triples = kwargs.get('transitions')
        delta = { a : SparseStateMatrix() for a in alp }
        for states, symbol, next_state in triples:
            ranked_sym = (symbol, len(states))
            delta[ranked_sym][states, next_state] = True
        return DTA(alp, states, acc, delta)

    def is_deterministic(self):
        pass

    def is_epsilon_free(self):
        pass

    def is_complete(self):
        pass

    def is_empty(self):
        pass

    def is_infinite(self):
        pass

    def reachable_states(self):
        pass

    def rename(self, state_homomorphism=None):
        pass

    def remove_unreachable_states(self):
        pass

    def set_error_state(self, error_state="err"):
        pass

    def generate_example(self):
        pass

    def generate(self):
        pass

    def myhill_nerode_classes(self):
        pass


    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return "<DTA states:%d>" % (len(self))

    def membership(self, tree):
        return self.parse(tree)[0]

    def parse(self, tree):
        for node in tree.bottom_up_traverse():
            ranked_sym = (node.label, tree.arity(node))
            if ranked_sym[1] == 0:
                node.state = self.delta[ranked_sym].det_transition(epsilon)
            else:
                ch = tuple(x.state for x in tree.children(node))
                node.state = self.delta[ranked_sym].det_transition(ch)

        if tree.root.state in self.accept_states:
            return Result.accept, tree.root.state
        else:
            return Result.reject, tree.root.state

    def determinize(self):
        pass

    def minimize(self):
        pass

    def product(self, other, acc_func, rej_func):
        pass

    def invert(self):
        pass

    def __copy__(self):
        pass

    def __and__(self, other):
        # intersection
        return self.product(other, operator.__and__, operator.__or__)

    def __or__(self, other):
        # union
        return self.product(other, operator.__or__, operator.__and__)

    def __xor__(self, other):
        # symmetric difference
        return self.product(other, operator.__xor__, operator.__eq__)

    def __le__(self, other):
        # subset
        pdfa = self.product(other, lambda x, y: x and not y,
                                   lambda x, y: not x or y)
        return pdfa.is_empty()

    def __ge__(self, other):
        # superset
        return other.issubset(self)

    def __eq__(self, other):
        # equality
        return self.__xor__(other).is_empty()

    def __ne__(self, other):
        # not equal
        return not self.__xor__(other).is_empty()

    def __sub__(self, other):
        # difference
        return self.__and__(other.complement())

    union = __or__
    intersection = __and__
    is_equal = __eq__
    issubset = __le__
    issuperset = __ge__
    difference = __sub__
    symmetric_difference = __xor__
    copy = __copy__
    complement = invert




class TestDTA(unittest.TestCase):
    def setUp(self):
        alp = [("and", 2), ("or", 2), ("not", 1), ("true", 0), ("false", 0)]
        states = ["T", "F"]
        acc = ["T"]
        rules = [(epsilon, "true", "T"), (epsilon, "false", "F"),
                 (("T", "T"), "and", "T"),
                 (("T", "F"), "and", "F"),
                 (("F", "T"), "and", "F"),
                 (("F", "F"), "and", "F"),
                 (("T", "T"), "or", "T"),
                 (("T", "F"), "or", "T"),
                 (("F", "T"), "or", "T"),
                 (("F", "F"), "or", "F"),
                 (("T",), "not", "F"),
                 (("F",), "not", "T")
                ]
        self.DTA = DTA.build(alphabet=alp, states=states, accept_states=acc,
                               transitions=rules)

    def test_DTA_membership(self):
        s = "and(or(and(true()false())true())and(true()or(false()true())))"
        tree = Tree.parse(s)
        tree.write_graphviz("test.txt")
        self.assertEqual(self.DTA.membership(tree), Result.accept)
        self.assertEqual(self.DTA.membership(Tree.parse("not(false())")),
                         Result.accept)


#    def test_generating_membership(self):
#        import automata.contextfree.cfg
#        cfg = automata.contextfree.cfg.ContextFreeGrammar("S")
#        cfg.add_rule("S -> expr")
#        cfg.add_rule("expr -> 'and(' expr expr ')'")
#        cfg.add_rule("expr -> 'or(' expr expr ')'")
#        cfg.add_rule("expr -> 'not(' expr ')'")
#        cfg.add_rule("expr -> 'true()'")
#        cfg.add_rule("expr -> 'false()'")
#        tree = Tree.parse(''.join(cfg.derive_random()))
#        print tree
#        tree.write_graphviz("test1.txt")
#        print self.DTA.membership(tree)
#        tree.write_graphviz("test2.txt")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDTA)
    unittest.TextTestRunner(verbosity=2).run(suite)
