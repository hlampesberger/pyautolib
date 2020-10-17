# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 15:52:24 2013

@author: hlampesberger
"""

from base import Result, mapping, epsilon, write_pdf, write_png
import ops
import nfa

import operator
import itertools
import collections

__all__ = ['DFA']

class DFA(object):
    def __init__(self, alphabet, states,
                 start, accept, reject,
                 delta, transitions=None, sink=None):
        self.alphabet = alphabet
        self.states = states
        self.start = start
        self.accept = accept
        self.reject = reject
        self.delta = delta
        self.transitions = transitions
        self.sink = sink
        # properties
        self._complete = None



    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return "<DFA states:%d complete:%d>" % (len(self), self.is_complete())

    @staticmethod
    def build(**kwargs):
        alp = kwargs.get('alphabet')
        if not isinstance(alp, set):
            alp = set(alp)
        assert(epsilon not in alp)
        states = set(kwargs.get('states'))
        acc = set(kwargs.get('accept_states'))
        rej = set(kwargs.get('reject_states'))
        start_state = kwargs.get('start_state')
        transitions = kwargs.get('transitions')
        sink = kwargs.get('sink', None)
        if sink is not None:
            if not (sink in states and sink in rej):
                raise RuntimeError("Invalid sink state!")
        tr = collections.defaultdict(lambda: sink)
        # tr = {(s, sym) : ns for s, sym, ns in transitions}
        for q, a, qn in transitions:
            tr[q, a] = qn
        # delta = lambda s, sym: tr.get((s, sym), sink)
        delta = lambda q, a: tr[q, a]
        return DFA(alp, states, start_state, acc, rej, delta, tr, sink)

    def rename(self, state_func=None, alp_func=None):
        if state_func is None:
            state_func = mapping()
        alp = None
        if alp_func is None:
            # identity
            alp_func = lambda x: x
            alp = self.alphabet
        else:
            alp = { alp_func(a) for a in self.alphabet}
        start = state_func(self.start)
        states = { state_func(s) for s in self.states }
        accept = { state_func(s) for s in self.accept }
        reject = { state_func(s) for s in self.reject }
        newsink = None
        if self.sink is not None:
            newsink = state_func(self.sink)
        tr = collections.defaultdict(lambda: newsink)
        for q, a, qn in self.itertransitions():
            tr[state_func(q), alp_func(a)] = state_func(qn)
        delta = lambda q, a: tr[q, a]
        return DFA(alp, states, start, accept, reject,
                   delta, tr, newsink)

    def parse(self, iterable):
        final = reduce(self.delta, iterable, self.start)
        if final in self.accept:
            return Result.accept, final
        elif final is None or final in self.reject:
            return Result.reject, final
        else:
            return Result.neutral, final

    def membership(self, iterable):
        return self.parse(iterable)[0]

    def successor(self, state):
        return {self.delta(state, sym) for sym in self.alphabet if \
                self.delta(state, sym) is not None}

    def predecessor(self, state):
        return {s for s in self.states for sym in self.alphabet \
                if self.delta(s, sym) == state}

    def generate_example(self):
        frontier = collections.deque()
        frontier.append((self.start, []))
        visited = set()
        while frontier:
            state, buf = frontier.popleft()
            visited.add(state)
            if state in self.accept:
                return buf
            else:
                # add neighbors
                for a in self.alphabet:
                    ns = self.delta(state, a)
                    if ns is not None and ns not in visited:
                        frontier.append((ns, buf + [a]))

    def reachable_states(self):
        visited = set()
        frontier = [ self.start ]
        while frontier:
            s = frontier.pop()
            visited.add(s)
            for ns in self.successor(s):
                if ns not in visited:
                    frontier.append(ns)
        return visited


    def dead_states(self):
        return {s for s in self.reject \
                if all(self.delta(s, sym) == s for sym in self.alphabet)}

    def is_complete(self):
        if self._complete is None:
            if any(self.delta(s, sym) is None \
            for s in self.states for sym in self.alphabet):
                self._complete = False
            else:
                self._complete = True
        return self._complete

    def is_empty(self):
        # depth first search from start to check whether an accepting state
        # is reachable or not
        frontier = [self.start]
        visited = set()
        while frontier:
            s = frontier.pop()
            if s in self.accept:
                # early exit
                return False
            visited.add(s)
            for ns in self.successor(s):
                if ns not in visited:
                    frontier.append(ns)
        return True

    def is_universal(self):
        # depth first search from start to check whether every reachable state
        # is accepting
        frontier = [self.start]
        visited = set()
        while frontier:
            s = frontier.pop()
            if s not in self.accept:
                # early exit
                return False
            visited.add(s)
            for ns in self.successor(s):
                if ns not in visited:
                    frontier.append(ns)
        return True

    # TODO: implement test for infiniteness
    def is_infinite(self):
        raise NotImplementedError

    def complete(self, sink= -1):
        if not self.is_complete():
            self.states.add(sink)
            self.reject.add(sink)
            oldsink = self.sink
            self.sink = sink
            if self.transitions is not None:
                # change default if transitions are still available
                for (q, a), qn in self.transitions.items():
                    if qn is oldsink:
                        self.transitions[q, a] = sink
                self.transitions.default_factory = lambda: sink
            else:
                d = self.delta
                # compose new delta function
                def new_delta(s, sym):
                    ns = d(s, sym)
                    if ns is not None:
                        return ns
                    else:
                        return sink
                self.delta = new_delta
            self._complete = True

    def del_states(self, states):
        assert(self.start not in states)
        if self.states & states:
            self.states -= states
            self.accept -= states
            self.reject -= states
            if self.transitions is not None:
                for (s, sym), ns in self.transitions.items():
                    if (s in states) or (ns in states):
                        del(self.transitions[s, sym])
                # repair delta default
                if self.sink in states:
                    self.sink = None
                    self.delta = lambda s, sym: \
                        self.transitions.get((s, sym), None)
            else:
                d = self.delta
                def new_delta(s, sym):
                    ns = d(s, sym)
                    if s in states or ns in states:
                        return None
                    else:
                        return ns
                self.delta = new_delta
            self._complete = None
        return self

    def del_unreachable_states(self):
        self.del_states(self.states - self.reachable_states())
        return self

    def del_dead_states(self):
        self.del_states(self.dead_states())
        return self

    def itertransitions(self):
        for s in self.states:
            for sym in self.alphabet:
                ns = self.delta(s, sym)
                if ns is not None:
                    yield  s, sym, ns

    def invert(self):
        tmp = self.accept
        self.accept = self.reject
        self.reject = tmp
        return self

    def reverse(self):
        A = nfa.NFA.viewDFA(self)
        return A.reverse().determinize()

    def myhill_nerode_equiv_classes(self):
        not_accepting_states = self.states - self.accept
        P = [set(self.accept), not_accepting_states]
        W = [set(self.accept), not_accepting_states]
        while W:
            S = W.pop()
            for a in self.alphabet:
                inv_states = {s for s in self.states if self.delta(s, a) in S}
                Pnew = []
                for R in P:
                    R1 = R & inv_states
                    if R1 and not (R.issubset(inv_states)):
                        R2 = R - R1
                        Pnew.append(R1)
                        Pnew.append(R2)
                        if R in W:
                            W.remove(R)
                            W.append(R1)
                            W.append(R2)
                        else:
                            W.append(min(R1, R2, key=len))
                    else:
                        Pnew.append(R)
                P = Pnew
        return {frozenset(s) for s in P}

    def minimize(self):
        self.complete()
        self.del_unreachable_states()
        eq_classes = self.myhill_nerode_equiv_classes()
        # construct new dfa with minimal states
        tr = collections.defaultdict(lambda: None)
        new_start = None
        new_accept = set()
        new_reject = set()

        # set_ref : States --> EquivClasses
        set_ref = dict()
        for c in eq_classes:
            for state in c:
                set_ref[state] = c

        # then add transitions
        for c in eq_classes:
            if self.start in c:
                if new_start is not None:
                    raise RuntimeError("Start state in multiple classes!")
                else:
                    new_start = c
            if c & self.accept:
                new_accept.add(c)
            elif c & self.reject:
                new_reject.add(c)
            # choose transitions from one representative
            for a in self.alphabet:
                for s in c:
                    tr[c, a] = set_ref[self.delta(s, a)]
                    # do it only for the first representative in c
                    break
        # delta = lambda s, sym: tr.get((s, sym), None)
        delta = lambda q, a: tr[q, a]
        return DFA(self.alphabet, eq_classes, new_start, new_accept,
                   new_reject, delta, tr)


    def _product(self, other, f_acc, f_rej):
        if self.alphabet != other.alphabet:
            raise RuntimeError("Incompatible alphabets")

        start = (self.start, other.start)
        alp = self.alphabet
        states = set()
        accept = set()
        reject = set()
        for s1, s2 in itertools.product(self.states, other.states):
            s = (s1, s2)
            states.add(s)
            if f_acc(s1 in self.accept, s2 in other.accept):
                accept.add(s)
            if f_rej(s1 in self.reject, s2 in other.reject):
                reject.add(s)
        # dereference from self
        d1 = self.delta
        d2 = other.delta
        delta = lambda s, sym: (d1(s[0], sym), d2(s[1], sym))
        return DFA(alp, states, start, accept, reject, delta)

    def __and__(self, other):
        # intersection
        return self._product(other, operator.__and__, operator.__or__)

    def __or__(self, other):
        # union
        return self._product(other, operator.__or__, operator.__and__)

    def __xor__(self, other):
        # symmetric difference
        return self._product(other, operator.__xor__, operator.__eq__)

    def __le__(self, other):
        # subset
        pdfa = self._product(other, lambda x, y: x and not y,
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

    def __copy__(self):
        tr = collections.defaultdict(lambda: self.sink)
        for q, a, qn in self.itertransitions():
            if qn is not self.sink:
                tr[q, a] = qn
        delta = lambda q, a: tr[q, a]
        return DFA(self.alphabet, set(self.states), self.start,
                   set(self.accept), set(self.reject),
                   delta, tr, self.sink)



    def __mul__(self, other):
        n1 = nfa.NFA.viewDFA(self)
        n2 = nfa.NFA.viewDFA(other)
        return (n1 * n2).determinize()

    # hopcroft karp naive algorithm
    def equivalent_states(self, other):
        def out(dfa, state):
            if state in dfa.accept:
                return Result.accept
            elif state in dfa.reject:
                return Result.reject
            else:
                return Result.neutral
        assert(self.is_complete() and other.is_complete())
        assert(self.alphabet == other.alphabet)
        rel = set()
        todo = collections.deque([(self.start, other.start)])
        # print len(self.alphabet), self.states, other.states
        while todo:
            pair = todo.popleft()
            if pair not in rel:
                if out(self, pair[0]) != out(other, pair[1]):
                    return set()
                else:
                    rel.add(pair)
                    todo.extend((self.delta(pair[0], a), other.delta(pair[1], a)) for a in self.alphabet)
        return rel



    union = __or__
    __add__ = __or__
    intersection = __and__
    is_equal = __eq__
    issubset = __le__
    issuperset = __ge__
    difference = __sub__
    symmetric_difference = __xor__
    copy = __copy__
    concat = __mul__
    complement = invert


    write_graphviz = ops.write_graphviz
    write_png = write_png
    write_pdf = write_pdf


