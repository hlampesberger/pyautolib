# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:27:02 2012

@author: hlampesberger
"""


import cProfile
import copy

from data.dataset import AnnotatedDataset, Dataset
from base import Result
from regular.oracle import MinAdequateTeacher
from learning.regular.lstar import build_lstar_DFA
from learning.regular.pta import build_PTA
from regular.ops import write_graphviz

def run():
    # datapath = "../testdata/fun.data"
    # ds = AnnotatedDataset.parse_sentence(labelspath, datapath)
    # ds = Dataset.parse_sentence(datapath)
    # ds = AnnotatedDataset.parse_ewsformat(labelspath, datapath)
    ds = AnnotatedDataset.parse_abbadingoformat("testdata/train173.txt")
    # ds = AnnotatedDataset.parse_abbadingoformat("../../testdata/RPNIAndEDSMDataSample.txt")
    oracle = MinAdequateTeacher.from_AnnotatedDataset(ds)
    pta = build_PTA(ds)
    dfa = build_lstar_DFA(oracle)
    print dfa
    print pta == dfa
    # eqdfa = pta.symmetric_difference(pta2)
    # print eqdfa
    # for i in eqdfa.generate():
    #    print i, pta.is_member(i), pta2.is_member(i)
    # pta.minimize()
    # print pta == pta2
    # print pta == pta3
    # print pta2 == pta3
    # for sample in ds:
    #    assert(pta.is_member(sample[0]) == sample[1])
    dfa.del_dead_states()
    dfa.write_png()
    # dfa.minimize().write_graphviz('test2.txt')
    # pta2.write_graphviz('test2.txt')
    # pta3.write_graphviz('test3.txt')
    # print pta
    # print pta2



if __name__ == '__main__':
    cProfile.run('run()')
