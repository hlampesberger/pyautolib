# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 09:54:21 2013

@author: hlampesberger
"""

from base import Result, mapping, write_pdf, write_png

import ops
import collections
import itertools
import operator

__all__ = ['DVPA']

class DVPA(object):
    # A = (\tilde{\Sigma}, Q, q_0, Q^F, \Gamma, \delta)
    # \tilde{\Sigma} = (\Sigma_{call}, \Sigma_{int}, \Sigma_{ret})
    #
    # important indices for alphabet, delta and transitions:
    # 0 ... call
    # 1 ... int
    # 2 ... ret
    def __init__(self, alp, states, start, accept,
                 stack_alp, delta, tr=None, sink=None):
        self.alphabet = alp
        self.states = states
        self.start = start
        self.accept = accept
        self.stack = stack_alp
        self.delta = delta
        self.tr = tr
        self.sink = sink
        # properties
        self._complete = None


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
        start = kwargs.get('start_state')
        acc = set(kwargs.get('accept_states'))

        tr_call = kwargs.get('call_transitions', [])
        tr_int = kwargs.get('int_transitions', [])
        tr_ret = kwargs.get('ret_transitions', [])
        sink = kwargs.get("sink", None)
        rand_stack_item = iter(stack).next()
        tr = (collections.defaultdict(lambda: (sink, rand_stack_item)),
              collections.defaultdict(lambda: sink),
              collections.defaultdict(lambda: sink))
        for q, a, q_next, gamma in tr_call:
            tr[0][q, a] = (q_next, gamma)
        for q, gamma, a, q_next in tr_ret:
            tr[2][q, gamma, a] = q_next
        for q, a, q_next in tr_int:
            tr[1][q, a] = q_next
        d_call = lambda q, a: tr[0][q, a]
        d_int = lambda q, a: tr[1][q, a]
        d_ret = lambda q, gamma, a: tr[2][q, gamma, a]
        delta = (d_call, d_int, d_ret)
        return DVPA(alp, states, start, acc, stack, delta, tr, sink)


    def __repr__(self):
        return "<VPA states:%d>" % (len(self.states))


    def rename(self, state_func=None, alp_func=None, stack_func=None):
        # states first
        if state_func is None:
            state_func = mapping()
        start = state_func(self.start)
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

        newsink = None
        if self.sink is not None:
            newsink = state_func(self.sink)
        rand_stack_item = iter(self.stack).next()
        tr = (collections.defaultdict(lambda: (newsink, rand_stack_item)),
              collections.defaultdict(lambda: newsink),
              collections.defaultdict(lambda: newsink))

        for q, a, qn, gamma in self.itercalls():
            if qn != self.sink:
                tr[0][state_func(q), alp_func[0](a)] = (state_func(qn),
                                                        stack_func(gamma))
        for q, a, qn in self.iterinterns():
            if qn != self.sink:
                tr[1][state_func(q), alp_func[1](a)] = state_func(qn)

        for q, gamma, a, qn in self.iterreturns():
            if qn != self.sink:
                tr[2][state_func(q), stack_func(gamma), alp_func[2](a)] = \
                    state_func(qn)
        delta_c = lambda q, a: tr[0][q, a]
        delta_i = lambda q, a: tr[1][q, a]
        delta_r = lambda q, gamma, a: tr[2][q, gamma, a]
        delta = (delta_c, delta_i, delta_r)
        return DVPA(alp, states, start, accept, stack, delta, tr, newsink)


    def int_step(self, q, s, a):
        return self.delta[1](q, a), s

    def call_step(self, q, s, a):
        qn, gamma = self.delta[0](q, a)
        s.append(gamma)
        return qn, s

    def ret_step(self, q, s, a):
        if s:
            # gamma =
            return self.delta[2](q, s.pop(), a), s
        else:
            return None, s

    def is_configuration_accepted(self, q, s):
        if q in self.accept and not s:
            return Result.accept
        else:
            return Result.reject

    def parse(self, sequence, stack=[]):
        q = self.start
        for a in sequence:
            if a in self.alphabet[0]:
                # call transition
                q, stack = self.call_step(q, stack, a)
            elif a in self.alphabet[1]:
                # int transition
                q, stack = self.int_step(q, stack, a)
            elif a in self.alphabet[2]:
                # ret transition
                q, stack = self.ret_step(q, stack, a)
            else:
                q = None
        return self.is_configuration_accepted(q, stack), q, stack


    def membership(self, sequence, stack=[]):
        return self.parse(sequence, stack)[0]

    def itercalls(self):
        if self.sink is None:
            for (q, c), (qn, gamma) in self.tr[0].items():
                yield q, c, qn, gamma
        else:
            for q in self.states:
                for c in self.alphabet[0]:
                    qn, gamma = self.delta[0](q, c)
                    if gamma is not None and qn is not None:
                        yield q, c, qn, gamma

    def iterinterns(self):
        if self.sink is None:
            for (q, a), qn in self.tr[1].items():
                yield q, a, qn
        else:
            for q in self.states:
                for a in self.alphabet[1]:
                    qn = self.delta[1](q, a)
                    if qn is not None:
                        yield q, a, qn

    def iterreturns(self):
        if self.sink is None:
            for (q, gamma, r), qn in self.tr[2].items():
                yield q, gamma, r, qn
        else:
            for q in self.states:
                for gamma in self.stack:
                    for r in self.alphabet[2]:
                        qn = self.delta[2](q, gamma, r)
                        if qn is not None:
                            yield q, gamma, r, qn

    def is_complete(self):
        if self._complete is None:
            for q in self.states:
                for a in self.alphabet[0]:
                    # complete on calls
                    qn, gamma = self.delta[0](q, a)
                    if qn is None or gamma is None:
                        print q, a, qn, gamma
                        self._complete = False
                        return False
                for a in self.alphabet[1]:
                    # complete on int
                    if self.delta[1](q, a) is None:
                        print q, a, qn, gamma
                        self._complete = False
                        return False
                for a in self.alphabet[2]:
                    # complete on returns
                    for gamma in self.stack:
                        if self.delta[2](q, gamma, a) is None:
                            self._complete = False
                            return False
            self._complete = True
        return self._complete

    def complete(self, sink= -1):
        if not self.is_complete():
            if sink not in self.states:
                self.states.add(sink)
            else:
                if sink in self.accept:
                    raise RuntimeError("Sink cannot be accepting state.")
            # repair links to old
            if self.tr is not None:
                for (q, a), (qn, gamma) in self.tr[0].items():
                    assert(gamma)
                    if qn is None:
                        self.tr[0][q, a] = sink, gamma
                for (q, a), qn in self.tr[1].items():
                    if qn is None:
                        self.tr[1][q, a] = sink
                for (q, gamma, a), qn in self.tr[2].items():
                    if qn is None:
                        self.tr[2][q, gamma, a] = sink
                # update default factories
                rand_stack_item = iter(self.stack).next()
                self.tr[0].default_factory = lambda: (sink, rand_stack_item)
                self.tr[1].default_factory = lambda: sink
                self.tr[2].default_factory = lambda: sink
                self.sink = sink
                self._complete = True
            else:
                # TODO: for the case when no transitions are available
                raise NotImplementedError("Only works when transitions are available")

    def _product(self, other, f_acceptance):
        for alp1, alp2 in zip(self.alphabet, other.alphabet):
            if alp1 != alp2:
                raise RuntimeError("Alphabets must be equal!")
        self.complete()
        other.complete()
        alp = self.alphabet
        start = (self.start, other.start)
        states = set()
        accept = set()
        stack = {(g1, g2) for g1, g2 in \
                 itertools.product(self.stack, other.stack)}
        for q1, q2 in itertools.product(self.states, other.states):
            q = (q1, q2)
            states.add(q)
            if f_acceptance(q1 in self.accept, q2 in other.accept):
                accept.add(q)
        delta1 = self.delta
        delta2 = other.delta
        def new_call(q, a):
            qn1, g1 = delta1[0](q[0], a)
            qn2, g2 = delta2[0](q[1], a)
            return (qn1, qn2), (g1, g2)
        new_int = lambda q, a: (delta1[1](q[0], a), delta2[1](q[1], a))
        new_ret = lambda q, g, a:(delta1[2](q[0], g[0], a),
                                  delta2[2](q[1], g[1], a))
        new_delta = (new_call, new_int, new_ret)
        return DVPA(alp, states, start, accept, stack, new_delta)

    def __and__(self, other):
        # intersection
        return self._product(other, operator.__and__)

    def __or__(self, other):
        # union
        return self._product(other, operator.__or__)


    write_graphviz = ops.write_graphviz
    write_png = write_png
    write_pdf = write_pdf
    union = __or__
    intersection = __and__






def profile():
    import time
    int_alphabet = ['0', '1']
    call_alphabet = ['<0', '<1']
    ret_alphabet = ['0>', '1>']
    Q = ['q0', 'q1']
    P = ['p0', 'p1']
    q0 = 'q0'
    Qf = Q
    calls = [('q0', '<1', 'q0', 'p0'),
             ('q0', '<0', 'q1', 'p0'),
             ('q1', '<1', 'q0', 'p1'),
             ('q1', '<0', 'q1', 'p1')]
    interns = [('q0', '0', 'q1'),
               ('q0', '1', 'q0'),
               ('q1', '0', 'q0'),
               ('q1', '1', 'q1')]
    returns = [('q0', 'p0', '1>', 'q0'),
               ('q0', 'p1', '1>', 'q1'),
               ('q1', 'p0', '0>', 'q0'),
               ('q1', 'p1', '0>', 'q1')]
    vpa = DVPA.build(call_alphabet=call_alphabet,
                         int_alphabet=int_alphabet,
                         ret_alphabet=ret_alphabet,
                         states=Q,
                         start_state=q0,
                         accept_states=Qf,
                         stack_alphabet=P,
                         call_transitions=calls,
                         int_transitions=interns,
                         ret_transitions=returns)
    s1 = "1.<0.1.<1.0.0.1>.0>.0.1.1.1".split('.') * 1000000
    stackmap = mapping()
    vpa.rename(stack_func=stackmap)
    t = time.time()
    vpa.membership(s1)
    t = time.time() - t
    print "finished ", (len(s1) / 1000000.0) / t, "MB/s"

# if __name__ == '__main__':
#    import cProfile
#    cProfile.run('profile()')
#    profile()
