# -*- coding: utf-8 -*-
"""
Created on Mon May 21 15:00:06 2012

@author: hlampesberger
"""

try:
    import numpy as np
except ImportError:
    import numpypy as np

__all__ = ['edit_distance', 'hamming_distance']

# levenstein distance between 2 strings
def edit_distance(target, source, ins_cost=1, sub_cost=2, del_cost=1):
    def ins(x): return ins_cost
    def sub(x1, x2):
        if x1 == x2:
            return 0
        else:
            return sub_cost

    def dele(x): return del_cost
    n = len(target)
    m = len(source)

    distance = np.zeros((n + 1) * (m + 1), np.int).reshape(n + 1, m + 1)
    for i in xrange(1, n + 1):
        distance[i, 0] = distance[i - 1, 0] + ins(target[i - 1])
    for j in xrange(1, m + 1):
        distance[0, j] = distance[0, j - 1] + dele(source[j - 1])

    for i in xrange(1, n + 1):
        for j in xrange(1, m + 1):
            distance[i, j] = min(distance[i - 1, j] + ins(target[i - 1]),
                                distance[i - 1, j - 1] + sub(source[j - 1], target[i - 1]),
                                distance[i, j - 1] + dele(source[j - 1]))

    # backtrack: follow from n,m back to 0,0 along the minimal path
    return distance[n, m]



def hamming_distance(s1, s2):
    minlen = min(len(s1), len(s2))
    return sum(map(lambda x, y: int(x is not y), \
                   s1[:minlen], s2[:minlen])) + \
           abs(len(s1) - len(s2))



