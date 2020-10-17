# -*- coding: utf-8 -*-
"""
Created on Wed May 30 14:32:07 2012

@author: hlampesberger
"""

import unittest
import collections
from regular.dfa import DFA
from base import Result, state_generator
from data.dataset import Dataset
from helper.stringops import k_grams, prefixes, prefix_symbol_suffix

__all__ = ['build_ktestable_DFA']


def _build_TSS_machine(k, dataset):
    prefix_set = set()
    suffix_set = set()
    segment_set = set()
    shorts_set = set()
    for sample in dataset:
        if len(sample[0]) < k:
            #
            shorts_set.add(tuple(sample[0]))
        if len(sample[0]) >= (k - 1):
            # prefix
            prefix_set.add(tuple(sample[0][:k - 1]))
            # suffix
            suffix_set.add(tuple(sample[0][-k + 1:]))
        if len(sample[0]) >= k:
            for gram in k_grams(k, sample[0]):
                segment_set.add(tuple(gram))
    return prefix_set, suffix_set, segment_set, shorts_set


def _build_DFA_from_TSS(alphabet, prefix_set, suffix_set, segment_set,
                        shorts_set):
    name_gen = state_generator()
    alp = set(alphabet)
    start_id = next(name_gen)
    reject = set()
    accept = set()
    tr = collections.defaultdict(lambda: None)
    state_map = {tuple() : start_id}

    prefshorts = prefix_set.union(shorts_set)

    for strng in prefshorts:
        for substrng in prefixes(strng):
            if substrng not in state_map:
                state_map[substrng] = next(name_gen)

    for strng in segment_set:
        if strng[1:] not in state_map:
            state_map[strng[1:]] = next(name_gen)
        if strng[:-1] not in state_map:
            state_map[strng[:-1]] = next(name_gen)

    for strng in prefshorts:
        for pref, sym, suff in prefix_symbol_suffix(strng):
            if not pref:
                tr[start_id, sym[0]] = state_map[sym]
            else:
                tr[state_map[pref], sym[0]] = state_map[pref + sym]

    for strng in segment_set:
        tr[state_map[strng[:-1]], strng[-1]] = state_map[strng[1:]]

    for strng in suffix_set.union(shorts_set):
        accept.add(state_map[strng])

    delta = lambda q, a: tr[q, a]
    return DFA(alp, set(state_map.values()),
               start_id, accept, reject, delta, tr)




def build_ktestable_DFA(k, dataset):
    # based on:
    # de la Higuera: Grammatical Inference (2010), p.  219-220
    if k < 2:
        raise AttributeError("The value of k must be >= 2!")
    tss = _build_TSS_machine(k, dataset)
    return _build_DFA_from_TSS(dataset.alphabet, *tss)


