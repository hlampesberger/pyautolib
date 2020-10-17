# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:27:02 2012

@author: hlampesberger
"""
from regular.ops import write_graphviz
from data.dataset import AnnotatedDataset
from learning.regular.gold import build_gold_DFA
import cProfile


def run():
    # ds = AnnotatedDataset.parse_abbadingoformat("../../testdata/RPNIAndEDSMDataSample.txt")
    ds = AnnotatedDataset.parse_custom("testdata/language.txt")
    # print ds
    # ds = AnnotatedDataset.parse_abbadingoformat("../testdata/train170.txt")
    # labelspath = "../testdata/lol.labels"
    # datapath = "../testdata/lol.data"
    # ds = AnnotatedDataset.parse_sentence(labelspath, datapath)
    dfa = build_gold_DFA(ds)
    dfa.write_png()
    for sample in ds:
        assert(dfa.membership(sample[0]) == sample[1])
    print dfa


if __name__ == '__main__':
    cProfile.run('run()')
