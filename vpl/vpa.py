# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 09:54:21 2013

@author: hlampesberger
"""

from base import Result, empty_set, mapping, write_png, write_pdf

import collections
import ops
import dvpa

__all__ = ['VPA']


class VPA(object):
    # A = (\tilde{\Sigma}, Q, q_0, Q^F, \Gamma, \delta)
    # \tilde{\Sigma} = (\Sigma_{call}, \Sigma_{int}, \Sigma_{ret})
    #
    # important indices for alphabet, delta and transitions:
    # 0 ... call
    # 1 ... int
    # 2 ... ret
    def __init__(self, alp, states, start, accept,
                 stack_alp, delta, tr=None):
        self.alphabet = alp
        self.states = states
        self.start = start
        self.accept = accept
        self.stack = stack_alp
        self.delta = delta
        self.tr = tr


    @staticmethod
    def build(**kwargs):
        call_alp = kwargs.get('call_alphabet', [])
        if not isinstance(call_alp, set):
            call_alp = set(call_alp)
        int_alp = kwargs.get('int_alphabet', [])
        if not isinstance(int_alp, set):
            int_alp = set(int_alp)
        ret_alp = kwargs.get('ret_alphabet', [])
        if not isinstance(ret_alp, set):
            ret_alp = set(ret_alp)
        stack = kwargs.get('stack_alphabet')
        if not isinstance(stack, set):
            stack = set(stack)
        alp = (call_alp, int_alp, ret_alp)

        states = set(kwargs.get('states'))
        start = set(kwargs.get('start_states'))
        acc = set(kwargs.get('accept_states'))

        tr_call = kwargs.get('call_transitions', [])
        tr_int = kwargs.get('int_transitions', [])
        tr_ret = kwargs.get('ret_transitions', [])
        tr = (collections.defaultdict(set), collections.defaultdict(set),
              collections.defaultdict(set))
        for q, a, q_next, gamma in tr_call:
            tr[0][q, a].add((q_next, gamma))
        for q, gamma, a, q_next in tr_ret:
            tr[2][q, gamma, a].add(q_next)
        for q, a, q_next in tr_int:
            tr[1][q, a].add(q_next)
        d_call = lambda q, a: tr[0][q, a]
        d_int = lambda q, a: tr[1][q, a]
        d_ret = lambda q, gamma, a: tr[2][q, gamma, a]
        delta = (d_call, d_int, d_ret)
        return VPA(alp, states, start, acc, stack, delta, tr)


    def __repr__(self):
        return "<VPA states:%d>" % (len(self.states))

    def rename(self, state_func=None, alp_func=None, stack_func=None):
        # states first
        if state_func is None:
            state_func = mapping()
        start = { state_func(s) for s in self.start }
        states = { state_func(s) for s in self.states }
        accept = { state_func(s) for s in self.accept }
        # alphabet x3
        alp = None
        if alp_func is None:
            # identity
            alp = self.alphabet
            alp_func = (lambda x: x, lambda x: x, lambda x: x)
        else:
            alp = ({alp_func[0](a) for a in self.alphabet[0]},
                   {alp_func[1](a) for a in self.alphabet[1]},
                   {alp_func[2](a) for a in self.alphabet[2]})
        # stack alphabet
        stack = None
        if stack_func is None:
            stack = self.stack
            stack_func = lambda x: x
        else:
            stack = { stack_func(gamma) for gamma in self.stack }

        tr = (collections.defaultdict(set),
              collections.defaultdict(set),
              collections.defaultdict(set))

        for q, a, qn, gamma in self.itercalls():
            tr[0][state_func(q), alp_func[0](a)].add((state_func(qn),
                                                    stack_func(gamma)))
        for q, a, qn in self.iterinterns():
            tr[1][state_func(q), alp_func[1](a)].add(state_func(qn))

        for q, gamma, a, qn in self.iterreturns():
            tr[2][state_func(q), stack_func(gamma), alp_func[2](a)].add(\
                    state_func(qn))
        delta_c = lambda q, a: tr[0][q, a]
        delta_i = lambda q, a: tr[1][q, a]
        delta_r = lambda q, gamma, a: tr[2][q, gamma, a]
        delta = (delta_c, delta_i, delta_r)
        return VPA(alp, states, start, accept, stack, delta, tr)


    def is_deterministic(self):
        if len(self.start) != 1:
            return False
        elif any(len(ns) > 1 \
                 for _, ns in self.tr[0].items()):
            return False
        elif any(len(ns) > 1 \
                 for _, ns in self.tr[1].items()):
            return False
        elif any(len(ns) > 1 \
                 for _, ns in self.tr[2].items()):
           return False
#        elif any(len(self.delta[0](q, a)) > 1 \
#               for q in self.states for a in self.alphabet[0]):
#            return False
#        elif any(len(self.delta[1](q, a)) > 1 \
#                 for q in self.states for a in self.alphabet[1]):
#            return False
#        elif any(len(self.delta[2](q, gamma, a)) > 1 \
#                 for q in self.states for a in self.alphabet[2] \
#                 for gamma in self.stack):
#           return False
        else:
            return True

    def int_step(self, conf, a):
        return {(ns, conf[1]) for ns in self.delta[1](conf[0], a)}

    def call_step(self, conf, a):
        return { (ns, conf[1] + (gamma,)) \
                 for ns, gamma in self.delta[0](conf[0], a) }

    def ret_step(self, conf, a):
        if len(conf[1]):
            return { (ns, conf[1][:-1]) \
                 for ns in self.delta[2](conf[0], conf[1][-1], a) }
        else:
            return empty_set


    def membership(self, sequence):
        state = {(s, tuple()) for s in self.start}
        for a in sequence:
            if a in self.alphabet[0]:
                # call transition
                state = {nc for c in state for nc in self.call_step(c, a)}
            elif a in self.alphabet[1]:
                # int transition
                state = {nc for c in state for nc in self.int_step(c, a)}
            elif a in self.alphabet[2]:
                # ret transition
                state = {nc for c in state for nc in self.ret_step(c, a)}
            # print a, state
        if any(c[0] in self.accept and len(c[1]) == 0 for c in state):
            return Result.accept
        else:
            return Result.reject


    def itercalls(self):
        for (q, c), ns in self.tr[0].items():
            for qn, gamma in ns:
                yield q, c, qn, gamma
#        for q in self.states:
#            for a in self.alphabet[0]:
#                for qn, gamma in self.delta[0](q, a):
#                    if gamma is not None and qn is not None:
#                        yield q, a, qn, gamma

    def iterinterns(self):
        for (q, a), ns in self.tr[1].items():
            for qn in ns:
                yield q, a, qn
#        for q in self.states:
#            for a in self.alphabet[1]:
#                for qn in self.delta[1](q, a):
#                    if qn is not None:
#                        yield q, a, qn

    def iterreturns(self):
        for (q, gamma, r), ns in self.tr[2].items():
            for qn in ns:
                yield q, gamma, r, qn
#        for q in self.states:
#            for gamma in self.stack:
#                for a in self.alphabet[2]:
#                    for qn in self.delta[2](q, gamma, a):
#                        yield q, gamma, a, qn



    def determinize(self):
        det = None
        if self.is_deterministic():
            rand_stack_item = iter(self.stack).next()
            tr = (collections.defaultdict(lambda: (None, rand_stack_item)),
                  collections.defaultdict(lambda: None),
                  collections.defaultdict(lambda: None))
            # just copy calls, ints and returns
            start = iter(self.start).next()
            for q, a, qn, gamma in self.itercalls():
                tr[0][q, a] = qn, gamma
            for q, a, qn in self.iterinterns():
                tr[1][q, a] = qn
            for q, gamma, a, qn in self.iterreturns():
                tr[2][q, gamma, a] = qn
            d_call = lambda q, a: tr[0][q, a]
            d_int = lambda q, a: tr[1][q, a]
            d_ret = lambda q, gamma, a: tr[2][q, gamma, a]
            delta = (d_call, d_int, d_ret)
            det = dvpa.DVPA(self.alphabet, self.states, start, self.accept,
                            self.stack, delta, tr)
        else:
            # Id function
            def Id(X):
                return {(x, x) for x in X}
            # projection of the 2nd component
            # proj = lambda new_q: new_q[1]
            def proj_set(S):
                return {x[1] for x in S}
            states = set()
            accept = set()
            start = frozenset(Id(self.start))
            stack = set()
            queue = collections.deque([start])
            tr = (collections.defaultdict(lambda: (None, None)),
                  collections.defaultdict(lambda: None),
                  collections.defaultdict(lambda: None))
            while queue:
                print "QUEUE", queue
                state = queue.popleft()
                states.add(state)
                if proj_set(state) & self.accept:
                    accept.add(state)
                for a in self.alphabet[1]:
                    # internal transitions
                    next_state = set()
                    for q, q2 in state:
                        for q1 in self.delta[1](q2, a):
                            next_state.add((q, q1))
                    if next_state:
                        s = frozenset(next_state)
                        print "FROM_INT", s
                        tr[1][state, a] = s
                        if s not in states:
                            queue.append(s)
                for a in self.alphabet[0]:
                    # call transitions
                    for gamma in self.stack:
                        R = {q1 for q in proj_set(state) \
                             for q1, g in self.delta[0](q, a) if g == gamma}
                        if R:
                            s = frozenset(Id(R))
                            print "FROM_CALL", s
                            sk = (state, a)
                            tr[0][state, a] = s, sk
                            stack.add(sk)
                            if s not in states:
                                queue.append(s)
                for a in self.alphabet[2]:
                    # return transitions
                    update = set()
                    for (sc, ac), (nsc, gc) in tr[0].items():
                        # already known call transitions
                        for q1, q2 in state:
                            for q in self.states:
                                if (q1, gc) in self.tr[0][q, ac]:
                                    for qn in self.delta(q2, a, gc):
                                        update.add((q, qn))


                    if update:
                        print "UPDATE1", update
                    update = {(q, qi) for q1, q2 in state \
                    for qi in self.states \
                    for gamma in self.stack \
                    for q, a1, qn, g1 in self.itercalls() \
                    for q2 in self.delta[2](q2, gamma, a) \
                    if g1 == gamma and qn == q1}
                    if update:
                        print "UPDATE2", update


#                    for gamma in self.stack:
#
#                        print "UPDATE", update
#                        if update:
#                            S2 = {(q, qi) for q, q2 in state \
#                            for q3, qi in update \
#                            if q2 == q3}
#                            print "S2", S2
#                            if S2:
#                                S2 = frozenset(S2)


            print
            print
            print stack
            print
            print tr[0]
            print
            print tr[1]
            print
            print tr[2]
            d_call = lambda q, a: tr[0][q, a]
            d_int = lambda q, a: tr[1][q, a]
            d_ret = lambda q, gamma, a: tr[2][q, gamma, a]
            delta = (d_call, d_int, d_ret)
            det = dvpa.DVPA(self.alphabet, states, accept, stack, delta, tr)
            # det.write_graphviz("test.png")
        return det

    write_graphviz = ops.write_graphviz
    write_png = write_png
    write_pdf = write_pdf


