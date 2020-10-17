# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 15:58:44 2012

@author: hlampesberger
"""

from data.otable import ObservationTable
from helper.stringops import prefixes


__all__ = ['build_lstar_DFA']



def _lstar_init(oracle):
    otable = ObservationTable(oracle.alphabet)
    otable.add_observation(tuple(), oracle.membership_query(tuple()))
    for a in oracle.alphabet:
        otable.add_observation((a,), oracle.membership_query((a,)))
    return otable


def _lstar_close_holes(otable, oracle):
    for hole in otable.hole_generator():
        # print "closing hole", hole
        query = hole[0] + hole[1]
        otable.add_observation(query, oracle.membership_query(query))


def _lstar_close(otable, oracle):
    state = otable.get_unclosed_state()
    while state is not None:
        otable.promote_state(state)
        _lstar_close_holes(otable, oracle)
        state = otable.get_unclosed_state()
    return True

def _lstar_consistent(otable, oracle):
    conflict = otable.get_inconsistency()
    while conflict is not None:
        exp = (conflict[0],) + conflict[1]
        otable.add_experiment(exp)
        _lstar_close_holes(otable, oracle)
        conflict = otable.get_inconsistency()
    return True

def _lstar_useeq(otable, oracle, eq_result):
    new_red_states = set(map(tuple, prefixes(eq_result[1])))
    otable.red_set.update(new_red_states)
    for p in new_red_states:
        for a in otable.alphabet:
            pa = p + (a,)
            if pa not in new_red_states:
                otable.blue_set.add(pa)
    _lstar_close_holes(otable, oracle)




def build_lstar_DFA(oracle):
    otable = _lstar_init(oracle)
    answer = False
    dfa = None
    # otable.print_table()
    closed = False
    consistent = False
    while not answer:
        # closed = otable.is_closed()
        # consistent = otable.is_consistent()
        while not closed or not consistent:
            if not closed:
                closed = _lstar_close(otable, oracle)
            if not consistent:
                consistent = _lstar_consistent(otable, oracle)
        # print
        # otable.print_table()
        # print otable

        dfa = otable.build_DFA()
        eq_result = oracle.equivalence_query(dfa)
        if not eq_result[0]:
            # print "not equal",
            _lstar_useeq(otable, oracle, eq_result)
            # print "added counterexample"
            closed = False
            consistent = False
        else:
            answer = True
    return dfa
    # otable.print_table()
