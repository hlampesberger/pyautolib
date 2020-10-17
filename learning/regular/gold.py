# -*- coding: utf-8 -*-
"""
Created on Fri Jun 01 12:37:09 2012

@author: hlampesberger
"""

from data.otable import ObservationTable
from pta import build_PTA

__all__ = ['build_gold_DFA']


def _gold_fillholes(otable):
    for p in otable.blue_set:
        r = otable.get_compatible_red_state(p)
        if r is not None:
            for e in otable.experiments:
                if otable(p, e) is not None:
                    # print r, e, p, otable(p, e), otable(tuple(), tuple())
                    otable.add_overlay(r, e, otable(p, e))
        else:
            return None
    for r in otable.red_set:
        for e in otable.experiments:
            if otable(r, e) == None:
                otable.add_overlay(r, e, 1)
    for p in otable.blue_set:
        r = otable.get_compatible_red_state(p)
        if r is not None:
            for e in otable.experiments:
                if otable(p, e) == None:
                    otable.add_overlay(p, e, otable(r, e))
        else:
            return None
    return otable


def build_gold_DFA(dataset):
    # based on:
    # de la Higuera: Grammatical Inference (2010), p.  250
    otable = ObservationTable(dataset.alphabet, dataset)

    od = True
    while od:
        # x = _get_obviously_different(otable)
        x = otable.get_unclosed_state()
        if x is not None:
            otable.promote_state(x)
        else:
            od = False

    otable = _gold_fillholes(otable)
    if otable is not None:
        # otable.print_table()
        return otable.build_DFA()
    else:
        print "gold: return pta"
        return build_PTA(dataset)

