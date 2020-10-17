# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:27:02 2012

@author: hlampesberger
"""


import cProfile

from data.dataset import AnnotatedDataset
from learning.regular.pta import build_PTA
from base import Result
from regular.ops import write_graphviz

def run():
    # labelspath = "../testdata/cms.01.labels"
    # datapath = "../testdata/cms.01.data"
    # labelspath = "../testdata/fun.labels"
    # datapath = "../testdata/fun.data"
    # ds = AnnotatedDataset.parse_sentence(labelspath, datapath)
    # ds = AnnotatedDataset.parse_abbadingoformat("../testdata/train170.txt")
    # ds = AnnotatedDataset.parse_ewsformat_bin(labelspath, datapath)
    ds = AnnotatedDataset.parse_abbadingoformat("testdata/RPNIAndEDSMDataSample.txt")
    pta = build_PTA(ds)
    # pta3 = pta.to_reverse_NFA().to_DFA().to_reverse_NFA().to_DFA()
    # pta.set_error_state()
    # print pta
    # print pta3 #89 states without error state --> 90
    # pta2 = pta.minimize()

    # print pta2
    # print pta == pta2

    # eqdfa = pta.symmetric_difference(pta2)
    # print eqdfa
    # for i in eqdfa.generate():
    #    print i, pta.is_member(i), pta2.is_member(i)
    # pta.minimize()
    # if not pta == pta2:
    #    print "not equal?"
    #    strng = (pta ^ pta2).shortest_example()
    #    print strng, pta.parse(strng), pta2.parse(strng)
    # else:
    #    print "equal"
    # print
    # for sample in ds:
    #    p = pta2.parse(sample[0])
    #    if p[0] != sample[1]:
    #        print p, sample
    # print pta == pta3
    # print pta2 == pta3
    # for sample in ds:
    #    assert(pta.is_member(sample[0]) == sample[1])
    # dfa = pta.minimize().rename().del_dead_states()
    dfa = pta
    dfa.write_png()
    # pta3.write_graphviz('test3.txt')
    # print pta
    # print pta2



if __name__ == '__main__':
    # run()
    cProfile.run('run()')
