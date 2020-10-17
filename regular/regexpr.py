# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 15:54:45 2013

@author: hlampesberger
"""

from base import Result, state_generator, epsilon

from helper.stringops import k_grams
import nfa
import collections
import pyparsing as pp

__all__ = ['RegExpr']


class RegExpr(object):
    def __init__(self, expression, alphabet=[], syntax="textbook",
                 whitespace=False):
        self.grammar_def = {"textbook": self._textbook_grammar,
                            "regex": self._regex_grammar}
        self.expression = expression
        self.whitespace = whitespace
        self.alphabet = set(alphabet)
        self.sgen = state_generator()
        self.states = set()
        self.start = None
        self.accept = None
        self.tr = collections.defaultdict(set)

        self.grammar = self.grammar_def[syntax]()

        self._dfa = None
        if expression:
            self.grammar.parseString(expression)
            self._dfa = self.mindfa()


    def __repr__(self):
        return "<RegExpr \"%s\">" % self.expression


    def _nfa(self):
        st = self.states
        acc = {self.accept}
        rej = self.states - acc
        start = {self.start}
        # delta = lambda s,a: self.tr.get((s, a), empty_set)
        delta = lambda q, a: self.tr[q, a]
        return nfa.NFA(self.alphabet, st, start, acc, rej, delta)

    def mindfa(self):
        if self._dfa is None:
            n = self._nfa()
            self._dfa = n.determinize().minimize().rename()
        return self._dfa

    def match(self, test):
        if self._dfa is None:
            self._dfa = self.mindfa()
        return self._dfa.membership(test) == Result.accept


    def _textbook_grammar(self):
        # terminals
        if self.whitespace:
            singleton = pp.Word(pp.alphanums).setParseAction(self._singleton)
        else:
            singleton = pp.Word(pp.alphanums,
                            exact=1).setParseAction(self._singleton)
        union = pp.Literal('+').suppress()
        star = pp.Literal('*').suppress()
        optional = pp.Literal('?').suppress()
        concatenation = pp.Literal('.').suppress()

        parser = pp.operatorPrecedence(singleton,
        [(star, 1, pp.opAssoc.LEFT, self._star),
         (optional, 1, pp.opAssoc.LEFT, self._optional),
         (pp.Optional(concatenation), 2, pp.opAssoc.LEFT,
          self._concatenation),
         (union, 2, pp.opAssoc.LEFT, self._union)]
        )
        return parser

    def _regex_grammar(self):
        # terminals
        singleton = pp.Word(pp.alphanums,
                            exact=1).setParseAction(self._singleton)
        union = pp.Literal('|').suppress()
        star = pp.Literal('*').suppress()
        iteration = pp.Literal('+').suppress()
        optional = pp.Literal('?').suppress()
        concatenation = pp.Literal('.').suppress()

        parser = pp.operatorPrecedence(singleton,
        [(star, 1, pp.opAssoc.LEFT, self._star),
         (iteration, 1, pp.opAssoc.LEFT, self._iteration),
         (optional, 1, pp.opAssoc.LEFT, self._optional),
         (pp.Optional(concatenation), 2, pp.opAssoc.LEFT, self._concatenation),
         (union, 2, pp.opAssoc.LEFT, self._union)]
        )
        return parser


    def _singleton(self, s, l, t):
        start = next(self.sgen)
        end = next(self.sgen)
        self.states.add(start)
        self.states.add(end)
        if self.start is None:
            self.start = start
        if self.accept is None:
            self.accept = end
        self.tr[start, t[0]].add(end)
        self.alphabet.add(t[0])
        # print "singleton", l, t, start, end
        return start, end

    def _star(self, s, l, t):
        start = next(self.sgen)
        end = next(self.sgen)
        self.states.add(start)
        self.states.add(end)
        if self.start == t[0][0][0]:
            self.start = start
        if self.accept == t[0][0][1]:
            self.accept = end
        self.tr[start, epsilon].add(t[0][0][0])
        self.tr[t[0][0][1], epsilon].add(end)
        self.tr[start, epsilon].add(end)
        self.tr[t[0][0][1], epsilon].add(t[0][0][0])
        # print "star", t, start, end
        return start, end

    def _iteration(self, s, l, t):
        start = next(self.sgen)
        end = next(self.sgen)
        self.states.add(start)
        self.states.add(end)
        if self.start == t[0][0][0]:
            self.start = start
        if self.accept == t[0][0][1]:
            self.accept = end
        self.tr[start, epsilon].add(t[0][0][0])
        self.tr[t[0][0][1], epsilon].add(end)
        self.tr[t[0][0][1], epsilon].add(t[0][0][0])
        # print "iteration", t, start, end
        return start, end

    def _concatenation(self, s, l, t):
        for first, second in k_grams(2, t[0]):
            if self.accept == first[1]:
                self.accept = second[1]
            self.tr[first[1], epsilon].add(second[0])
        # print "concat", t, t[0][0][0], t[0][-1][1]
        return t[0][0][0], t[0][-1][1]

    def _union(self, s, l, t):
        start = next(self.sgen)
        end = next(self.sgen)
        self.states.add(start)
        self.states.add(end)
        for subexpr in t[0]:
            s, e = subexpr
            if self.start == s:
                self.start = start
            if self.accept == e:
                self.accept = end
            self.tr[start, epsilon].add(s)
            self.tr[e, epsilon].add(end)
        # print "union", t, start, end
        return start, end

    def _optional(self, s, l, t):
        start = next(self.sgen)
        end = next(self.sgen)
        self.states.add(start)
        self.states.add(end)
        if self.start == t[0][0][0]:
            self.start = start
        if self.accept == t[0][0][1]:
            self.accept = end
        self.tr[start, epsilon].add(t[0][0][0])
        self.tr[t[0][0][1], epsilon].add(end)
        self.tr[start, epsilon].add(end)
        # print "optional", t, start, end
        return start, end




def speed_comp():
    import time
    import re
    n = 1000
    for i in xrange(1, 40):

        strng = "a?"*i + "a"*i
        test = "a"*i
        print "test", i, strng
        t = time.time()
        r = RegExpr(strng)
        for j in xrange(n):
            r.match(test)
        print "DFA", time.time() - t
        t = time.time()
        r = re.compile(strng)
        for j in xrange(n):
            r.match(test)
        print "RE ", time.time() - t





if __name__ == '__main__':
    r = RegExpr("e+m")
    r.mindfa().write_png("test")
#    import cProfile
#    cProfile.run("speed_comp()")
#    speed_comp()

