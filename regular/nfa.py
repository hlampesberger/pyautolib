# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 15:52:37 2013

@author: hlampesberger
"""


from base import Result, epsilon, mapping, empty_set, write_png, write_pdf
import ops
import dfa

import collections
import itertools

__all__ = ['NFA']


class NFA(object):
    def __init__(self, alphabet, states,
                 start_states, accept, reject,
                 delta, transitions=None):
        self.alphabet = alphabet
        self.states = states
        self.start = start_states
        self.accept = accept
        self.reject = reject
        self.delta = delta
        self.transitions = transitions
        # properties
        self._epsilon_free = None
        self._is_deterministic = None
        self._closure = None
        self._complete = None


    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return "<NFA states:%d eps_free:%d det:%d>" \
               % (len(self), self.is_epsilon_free(), self.is_deterministic())

    @staticmethod
    def build(**kwargs):
        alp = kwargs.get('alphabet')
        if not isinstance(alp, set):
            alp = set(alp)
        assert(epsilon not in alp)
        states = set(kwargs.get('states'))
        acc = set(kwargs.get('accept_states'))
        rej = set(kwargs.get('reject_states'))
        start_states = set(kwargs.get('start_states'))
        assert(len(states & start_states) > 0)
        transitions = kwargs.get('transitions')
        tr = collections.defaultdict(set)
        for s, sym, ns in transitions:
            assert(s in states)
            assert(ns in states)
            tr[s, sym].add(ns)
        delta = lambda q, a: tr[q, a]
        return NFA(alp, states, start_states, acc, rej, delta, tr)

    @classmethod
    def viewDFA(cls, dfa):
        def new_delta(s, sym):
            ns = dfa.delta(s, sym)
            if ns is not None:
                return {ns}
            else:
                return empty_set
        return NFA(dfa.alphabet, dfa.states, {dfa.start}, dfa.accept,
                   dfa.reject, new_delta)

    def rename(self, state_func=None, alp_func=None):
        if state_func is None:
            state_func = mapping()
        if alp_func is None:
            # identity
            alp_func = lambda x: x
        start = { state_func(s) for s in self.start }
        states = { state_func(s) for s in self.states }
        accept = { state_func(s) for s in self.accept }
        reject = { state_func(s) for s in self.reject }
        tr = collections.defaultdict(set)
        for s, a, ns in self.itertransitions():
            tr[state_func(s), alp_func(a)].add(state_func(ns))
        delta = lambda s, a: tr.get((s, a), empty_set)
        return NFA(self.alphabet, states, start, accept, reject, delta, tr)

    def closure(self):
        # based on:
        # de la Higuera: Grammatical Inference (2010), p. 73, Algorithm 4.1
        if self._closure is None:
            self._closure = collections.defaultdict(set)
            for i in self.states:
                for j in self.states:
                    if i == j:
                        self._closure[i].add(j)
                    else:
                        if j in self.delta(i, epsilon):
                            self._closure[i].add(j)
            for k in self.states:
                for i in self.states:
                    for j in self.states:
                        if k in self._closure[i] and j in self._closure[k]:
                            self._closure[i].add(j)
        return self._closure

    def membership(self, sequence):
        # SLOW implementation!
        cl = self.closure()
        q = set(self.start)
        for a in sequence:
            # epsilons first
            qc = set()
            for s in q:
                qc.update(cl[s])
            qn = set()
            for s in qc:
                qn.update(self.delta(s, a))
            q = qn

        # for closure
        final = set()
        for s in q:
            final.update(cl[s])
        if final:
            if final & self.accept:
                return Result.accept
            elif final & self.reject:
                return Result.reject
            else:
                return Result.neutral
        else:
            return Result.reject


    def reverse(self):
        tmp = set(self.start)
        start = set(self.accept)
        accept = tmp
        reject = self.reject | self.accept - tmp
        # start state cannot be accept and reject both
        tr = collections.defaultdict(set)
        for s, a, ns in self.itertransitions():
            tr[ns, a].add(s)
        delta = lambda s, sym: tr.get((s, sym), empty_set)
        return NFA(self.alphabet, set(self.states), start,
                   accept, reject, delta, tr)

    def is_epsilon_free(self):
        if self._epsilon_free is None:
            self._epsilon_free = all(a != epsilon for (_, a, _) \
                                         in self.itertransitions())
        return self._epsilon_free

    def is_deterministic(self):
        if self._is_deterministic is None:
            self._is_deterministic = \
               len(self.start) == 1 and \
               self.is_epsilon_free() and \
               all(len(self.delta(s, a)) <= 1 \
                   for s in self.states for a in self.alphabet)
        return self._is_deterministic

    def itertransitions(self):
        for s in self.states:
            for a in self.alphabet:
                for ns in self.delta(s, a):
                    yield s, a, ns
            for ns in self.delta(s, epsilon):
                yield s, epsilon, ns




    def determinize(self):
        # based on:
        # Subset Construction presented by Ullman (Automata course)
        # extended with closure operation to work with epsilon transitions

        # if not self.is_complete():
        #    self.set_error_state()

        closure = None
        if not self.is_epsilon_free():
            closure = self.closure()

        dfa_accept = set()
        dfa_reject = set()

        if closure is None:
            start = frozenset(self.start)
        else:
            start = frozenset({ x for s in self.start \
                                  for x in closure[s] })

        dfa_states = { start }
        tr = collections.defaultdict(lambda: None)

        queue = collections.deque([ start ])
        if start & self.accept:
            dfa_accept.add(start)
        elif start & self.reject:
            dfa_reject.add(start)

        while queue:
            curr_state = queue.popleft()
            for a in self.alphabet:
                next_direct = { x for s in curr_state \
                                  for x in self.delta(s, a) }
                if closure is None:
                    next_state = frozenset(next_direct)
                else:
                    next_state = frozenset({ x for s in next_direct \
                                               for x in closure[s] })

                if next_state:
                    if next_state not in dfa_states:
                        dfa_states.add(next_state)
                        queue.append(next_state)

                    tr[curr_state, a] = next_state
                    if next_state & self.accept:
                        dfa_accept.add(next_state)
                    elif next_state & self.reject:
                        dfa_reject.add(next_state)
        # dfa_delta = lambda s,a: tr.get((s, a), None)
        dfa_delta = lambda q, a: tr[q, a]
        return dfa.DFA(self.alphabet, dfa_states, start, dfa_accept,
                      dfa_reject, dfa_delta, tr)




    def __mul__(self, other):
        # concat self * other
        if self.alphabet != other.alphabet:
            raise RuntimeError("Alphabets must be equal")
        states = {(0, s) for s in self.states} | \
                  {(1, s) for s in other.states}
        start = {(0, s) for s in self.start}
        reject = {(0, s) for s in self.reject} | \
                 {(1, s) for s in other.reject}
        accept = {(1, s) for s in other.accept}

        tr = collections.defaultdict(set)
        for s, a, ns in self.itertransitions():
            tr[(0, s), a].add((0, ns))
        for s, a, ns in other.itertransitions():
            tr[(1, s), a].add((1, ns))
        for s0, s1 in itertools.product(self.accept, other.start):
            tr[(0, s0), epsilon].add((1, s1))
        delta = lambda s, a: tr.get((s, a), empty_set)
        return NFA(self.alphabet, states, start, accept,
                   reject, delta, tr)

    write_graphviz = ops.write_graphviz
    write_png = write_png
    write_pdf = write_pdf


