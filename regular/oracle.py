# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 15:58:44 2012

@author: hlampesberger
"""
from base import Result
from learning.regular.pta import build_PTA

__all__ = ['MinAdequateTeacher']

class MinAdequateTeacher(object):
    def __init__(self, target):
        self.target = target
        self.alphabet = target.alphabet

    def membership_query(self, query):
        result = self.target.membership(query)
#        if result == Result.neutral:
#            raise RuntimeError("This should never happen")
        return result == Result.accept

    def equivalence_query(self, query):
        # print len(self.target.alphabet), len(query.alphabet)
        pdfa = self.target ^ query
        if pdfa.is_empty():
            return True, [], Result.neutral
        else:
            # pdfa = self.target ^ query
            strng = pdfa.generate_example()
            return False, strng, self.target.membership(strng)

    @staticmethod
    def from_AnnotatedDataset(ds):
        dfa = build_PTA(ds)
        return MinAdequateTeacher(dfa.minimize())


