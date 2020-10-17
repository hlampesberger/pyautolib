# -*- coding: utf-8 -*-
"""
Created on Tue Jun 05 10:32:08 2012

@author: hlampesberger
"""

import copy
import collections
import math

from base import Result
from pta import build_PTA
from regular.ops import merge, promote

__all__ = ['build_edsm_DFA']




def _edsm_count(dfa, dataset):
    # TODO: verify how to count bad transitions
    tp = collections.Counter()
    tn = collections.Counter()
    for sample in dataset:
        res = dfa.parse(sample[0])[1]
        # print res
        if sample[1] == Result.accept:
            tp[res] += 1
        else:
            tn[res] += 1
#    tp = collections.Counter([ dfa.parse(x[0])[1] \
#                               for x in dataset.filter(Result.accept) ])
#    tn = collections.Counter([ dfa.parse(x[0])[1] \
#                               for x in dataset.filter(Result.reject) ])
    sc = 0.0
    for q in dfa.states:
        if not math.isinf(-sc):
            if tn[q] > 0:
                if tp[q] > 0:
                    sc = -float('inf')
                else:
                    sc += tn[q] - 1
            else:
                if tp[q] > 0:
                    sc += tp[q] - 1
    return sc


def build_edsm_DFA(dataset, accept_dtype=1, reject_dtype=0):
    neg_dataset = dataset.filter(reject_dtype)
    pos_dataset = dataset.filter(accept_dtype)
    dfa = build_PTA(pos_dataset)
    red, blue, order = promote(dfa, set(), set(), dfa.start, None,
                               update_order=False)

    while blue:
        promotion = False
        for b in blue:
            if not promotion:
                bs = -float('inf')
                atleastonemerge = False
                for r in red:
                    s = _edsm_count(merge(copy.copy(dfa), r, b), dataset)
                    if s > -float('inf'):
                        atleastonemerge = True
                    if s > bs:
                        bs = s
                        qr = r
                        qb = b
                if not atleastonemerge:
                    red, blue, order = promote(dfa, red, blue, b, None,
                                               update_order=False)
                    promotion = True
                    break

            if not promotion:
                merge(dfa, qr, qb)
                blue = set()
                for r in red:
#                    succ = { ns for sp in dfa.delta.values() \
#                             for ns in sp.successors(r) }
                    succ = dfa.successor(r)
                    update_set = succ - red
                    blue.update(update_set)

    for sample in neg_dataset:
        res, state = dfa.parse(sample[0])
        if state is not None:
            dfa.reject.add(state)
    for sample in pos_dataset:
        res, state = dfa.parse(sample[0])
        if state is not None:
            dfa.accept.add(state)
        else:
            print "There is something wrong"
    dfa.del_unreachable_states()

    return dfa



