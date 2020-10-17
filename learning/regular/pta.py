# -*- coding: utf-8 -*-
"""
Created on Mon May 21 12:23:41 2012

@author: hlampesberger
"""

import collections

from regular.dfa import DFA
from base import state_generator
from data.dataset import AnnotatedDataset



__all__ = ['build_PTA']


def build_PTA(dataset):
    # based on:
    # de la Higuera: Grammatical Inference (2010), p.  239, Algorithm 12.1
    labels_available = isinstance(dataset, AnnotatedDataset)
    name_generator = state_generator()
    start = next(name_generator)
    states = { start }
    alp = dataset.alphabet
    accept = set()
    reject = set()
    tr = collections.defaultdict(lambda: None)
    for sample in dataset:
        curr_state = start
        for symbol in sample[0]:
            next_state = tr.get((curr_state, symbol), None)
            if next_state is None:
                next_state = next(name_generator)
                states.add(next_state)
                tr[curr_state, symbol] = next_state
            curr_state = next_state
        if labels_available:
            if sample[1]:
                accept.add(curr_state)
            else:
                reject.add(curr_state)
        else:
            accept.add(curr_state)
    # delta = lambda s, a: tr.get((s, a), None)
    delta = lambda q, a: tr[q, a]
    return DFA(alp, states, start, accept, reject, delta, tr)

