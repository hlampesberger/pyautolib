# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 12:47:50 2012

@author: hlampesberger
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 10:12:09 2012

@author: hlampesberger
"""


import unittest


from data.tree import Tree
from base import Result
from regular.regexpr import RegExpr

__all__ = ['UTA']

epsilon = ""

# unranked tree automaton
class UTA(object):
    def __init__(self, alphabet, states, accept_states, delta):
        self.alphabet = alphabet
        self.states = states
        self.accept_states = accept_states
        self.delta = delta

    @staticmethod
    def build(**kwargs):
        alp = set(kwargs.get('alphabet'))
        states = set(kwargs.get('states'))
        acc = set(kwargs.get('accept_states'))
        triples = kwargs.get('transitions')
        delta = { a : dict() for a in alp }
        for symbol, regex, next_state in triples:
            if regex != epsilon:
                delta[symbol][RegExpr(regex, alphabet=states,
                                      whitespace=True).mindfa()] = next_state
            else:
                delta[symbol][epsilon] = next_state
        return UTA(alp, states, acc, delta)

    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return "<DRTA states:%d>" % (len(self))


    def _get_state(self, tree):
        ranked_sym = (tree.label, tree.arity())
        if ranked_sym[1] == 0:
            return self.delta[ranked_sym].det_transition(epsilon)
        else:
            return self.delta[ranked_sym].det_transition(\
                   tuple(self._get_state(n) for n in tree.children))

    def membership(self, tree):
        return self.parse(tree)[0]


    def parse(self, tree):
        for node in tree.bottom_up_traverse():
            if tree.is_leaf(node):
                node.state = self.delta[node.label][epsilon]
            else:
                ch = [x.state for x in tree.children(node)]
                for dfa, next_state in self.delta[node.label].items():
                    if dfa.membership(ch) == Result.accept:
                        node.state = next_state
                        break

        if tree.root.state in self.accept_states:
            return Result.accept, tree.root.state
        else:
            return Result.reject, tree.root.state

    def determinize(self):
        pass

    def minimize(self):
        pass

    def product(self, other):
        pass








class TestUTA(unittest.TestCase):
    def setUp(self):
        alp = ["and", "or", "true", "false", 'not']
        states = ["T", "F"]
        acc = ["T"]
        rules = [("true", epsilon, "T"), ("false", epsilon, "F"),
                 ("and", "T T*", "T"),
                 ("and", "(T + F)* F (T + F)*", "F"),
                 ("or", "F F*", "F"),
                 ("or", "(T + F)* T (T + F)*", "T"),
                 ("not", "T", "F"),
                 ("not", "F", "T")
                ]
        self.duta = UTA.build(alphabet=alp, states=states, accept_states=acc,
                               transitions=rules)

    def test_duta_membership(self):
        s = "and(or(and(true()false())true())and(true()or(false()true()true()false())))"
        tree = Tree.parse(s)
        # print tree
        # print self.drta.membership(tree)
        self.assertEqual(self.duta.membership(tree), Result.accept)


#    def test_generating_membership(self):
#        import automata.contextfree.cfg
#        cfg = automata.contextfree.cfg.ContextFreeGrammar("S")
#        cfg.add_rule("S -> expr")
#        cfg.add_rule("expr -> 'and' '(' expr expr ')'")
#        # cfg.add_rule("expr -> 'and' '(' expr expr expr ')'")
#        cfg.add_rule("expr -> 'or' '(' expr expr ')'")
#        # cfg.add_rule("expr -> 'or' '(' expr expr expr ')'")
#        cfg.add_rule("expr -> 'not' '(' expr ')'")
#        cfg.add_rule("expr -> 'true()'")
#        cfg.add_rule("expr -> 'false()'")
#        tree = Tree.parse(''.join(cfg.derive_random()))
#        print tree
#        print self.duta.membership(tree)
#        tree.write_graphviz("test.txt")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUTA)
    unittest.TextTestRunner(verbosity=2).run(suite)
