# -*- coding: utf-8 -*-
"""
Created on Tue Jun 05 16:35:17 2012

@author: hlampesberger
"""

import collections
import itertools
from dataset import AnnotatedDataset
from helper.stringops import suffixes
from base import state_generator
from regular.dfa import DFA

__all__ = ['ObservationTable']


def _compare_exp(val_u, val_v):
    if val_u == None or val_v == None:
        return True
    else:
        return val_u == val_v


class ObservationTable(object):
    def __init__(self, alphabet, dataset=None):
        self.alphabet = alphabet
        self._mq = dict()
        self.red_set = set([tuple()])
        self.blue_set = set([(x,) for x in self.alphabet])
        self.experiments = set([tuple()])
        self._overlay = collections.defaultdict(lambda: collections.defaultdict(lambda: None))

        if dataset:
            assert(isinstance(dataset, AnnotatedDataset))
            for sample in dataset:
                for exp in map(tuple, suffixes(sample[0])):
                    # print exp
                    self.add_experiment(exp)
                self.add_observation(*sample)


    def get_hole(self):
        # implicitly checks if table is complete
        for state in self.red_set | self.blue_set:
            for exp in self.experiments:
                if self(state, exp) is None:
                    return state, exp
        return None

    def hole_generator(self):
        for state in self.red_set | self.blue_set:
            for exp in self.experiments:
                if self(state, exp) is None:
                    yield state, exp

    def get_unclosed_state(self):
        # implicitly checks if table is closed
        for blue in self.blue_set:
            res = map(lambda x: self.states_compatible(blue, x), self.red_set)
            if not any(res):
                return blue
        return None

    def get_inconsistency(self):
        for s1, s2 in itertools.combinations(self.red_set, 2):
            if self.states_compatible(s1, s2):
                for a in self.alphabet:
                    for exp in self.experiments:
                        if self(s1 + (a,), exp) != self(s2 + (a,), exp):
                            return a, exp
        return None

    def is_closed(self):
        return self.get_unclosed_state() is None

    def is_complete(self):
        return self.get_hole() is None

    def is_consistent(self):
        if self.is_closed() and self.is_complete():
            for s1, s2 in itertools.combinations(self.red_set, 2):
                if self.states_compatible(s1, s2):
                    res = map(lambda a: self.states_compatible(s1 + (a,),
                                        s2 + (a,)), self.alphabet)
                    if not all(res):
                        return False
            return True
        else:
            return False

    def get_compatible_red_state(self, blue):
        for r in self.red_set:
            if self.states_compatible(r, blue):
                return r
        return None


    def states_compatible(self, st1, st2):
        vec = map(lambda x: _compare_exp(self(st1, x), self(st2, x)),
                       self.experiments)
        return all(vec)

    def promote_state(self, state):
        if state in self.blue_set:
            self.red_set.add(state)
            self.blue_set.discard(state)
            for sym in [(x,) for x in self.alphabet]:
                self.blue_set.add(state + sym)
        else:
            raise RuntimeError("Cannot promote a state that is not in blue")

    def add_observation(self, observation, label):
        tobs = tuple(observation)
        if tobs in self._mq:
            if self._mq[tobs] is not None:
                if label != self._mq[tuple(observation)]:
                    raise RuntimeError("Conflict in query table: %s" % \
                                       str(observation))
            else:
                self._mq[tuple(observation)] = label
        else:
            self._mq[tuple(observation)] = label


    def add_experiment(self, exp):
        self.experiments.add(exp)
        # self.add_observation(observation, label)


    def add_overlay(self, state, experiment, label):
        self._overlay[state][experiment] = label

    def get_observation(self, u, v):
        tup = u + v
        if tup in self._mq:
            return self._mq.get(u + v)
        elif u in self._overlay:
            if v in self._overlay[u]:
                return self._overlay[u][v]
        else:
            return None
    __call__ = get_observation

    def build_DFA(self):
        # observation table must be closed and complete!
        state_map = dict()
        name_gen = state_generator()
        for v in sorted(self.red_set, key=len):
            unique = True
            for r in sorted(state_map.keys(), key=len):
                # check if there exists a compatible red state
                # in gold algorithm, this can never happen
                # but in lstar it can
                if self.states_compatible(r, v):
                    unique = False
                    state_map[v] = state_map[r]
            if unique:
                state_map[v] = next(name_gen)
        states = set(state_map.values())
        accept = set()
        reject = set()
        start = state_map[tuple()]
        tr = collections.defaultdict(lambda: None)
        for r in self.red_set:
            if self(r, tuple()) == 1:
                accept.add(state_map[r])
            else:
                reject.add(state_map[r])

        for q in self.red_set:
            for sym in self.alphabet:
                for u in self.red_set:
                    if self.states_compatible(u, q + (sym,)):
                        tr[state_map[q], sym] = state_map[u]
        # print states, accept_states, reject_states
        delta = lambda q, a: tr[q, a]
        return DFA(set(self.alphabet), states, start, accept, reject, delta)


    def print_table(self):
        exp = sorted(self.experiments)
        print "exp", "-"*72
        for i, e in enumerate(exp):
            print  "%d:%s" % (i + 1, str(e)),
        print
        print "red", "-"*72
        for r in sorted(self.red_set):
            print r, "|:",
            for e in exp:
                print self(r, e),
            print
        print "blue", "-"*72
        for p in sorted(self.blue_set):
            print p, "|:",
            for e in exp:
                print self(p, e),
            print

    def __repr__(self):
        return "<ObservationTable exp:%d red:%d blue:%d mq:%d>" % \
        (len(self.experiments), len(self.red_set), len(self.blue_set),
         len(self._mq))


