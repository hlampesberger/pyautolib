# -*- coding: utf-8 -*-
"""
Created on Tue Jun 05 10:32:08 2012

@author: hlampesberger
"""

import copy

from base import Result
from pta import build_PTA
from regular.ops import merge, choose, promote

__all__ = ['build_rpni_DFA']

def _rpni_compatible(dfa, neg_dataset):
    return all(map(lambda x: dfa.membership(x[0]) != Result.accept,
                       neg_dataset))



def build_rpni_DFA(dataset, accept_dtype=1, reject_dtype=0):
    ppta = build_PTA(dataset.filter(accept_dtype))
    # write_graphviz(ppta, "test.txt")
    order = {}
    red, blue, order = promote(ppta, set(), set(), ppta.start, order)
    neg_dataset = dataset.filter(reject_dtype)
    while blue:
        # print red, blue
        blue_state = choose(blue, order)
        compatible_found = False
        for r in red:
            mdfa = merge(copy.copy(ppta), r, blue_state)
            if _rpni_compatible(mdfa, neg_dataset):
                compatible_found = True
                ppta = mdfa
                blue = set()
                order["blue"] = {}
                for r in red:
                    # succ = { ns for sp in ppta.delta.values() \
                    #         for ns in sp.successors(r) }
                    succ = ppta.successor(r)
                    update_set = succ - red
                    for b in update_set:
                        order["blue"][b] = order["red"][r] + 1
                    blue.update(update_set)

        if not compatible_found:
            # print "PROMOTE"
            red, blue, order = promote(ppta, red, blue, blue_state, order)
        # ppta.write_graphviz("test2.txt")

    for sample in neg_dataset:
        res, state = ppta.parse(sample[0])
        if state is not None:
            ppta.reject.add(state)

    ppta.del_unreachable_states()

    return ppta

