# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 19:17:18 2013

@author: harald
"""

__all__ = ['k_grams', 'prefixes', 'suffixes', 'prefix_symbol_suffix']


def k_grams(k, lst):
    for i in xrange(len(lst) - k + 1):
        yield lst[i:i + k]

def prefixes(lst):
    for i in xrange(1, len(lst) + 1):
        yield lst[:i]

def suffixes(lst):
    for i in xrange(len(lst)):
        yield lst[i:]

def prefix_symbol_suffix(lst):
    for i in xrange(1, len(lst) + 1):
        yield lst[0:i - 1], lst[i - 1:i], lst[i:]

# def prefix_closed_set(dataset):
#    return reduce(lambda s,x: s.union(map(tuple, prefixes(x[0]))), dataset, set())

# def suffix_closed_set(dataset):
#    return reduce(lambda s,x: s.union(map(tuple, suffixes(x[0]))), dataset, set())


