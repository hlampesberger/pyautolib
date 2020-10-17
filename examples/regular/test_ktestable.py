# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:27:02 2012

@author: hlampesberger
"""

from data.dataset import Dataset, AnnotatedDataset
from learning.regular.ktestable import build_ktestable_DFA
from base import Result

from regular.ops import write_graphviz
import cProfile


def run():
    # labelspath = "../testdata/cms.01.labels"
    # datapath = "../testdata/cms.01.data"
    # datapath = "../testdata/fun.data"
    # labelspath = "../testdata/fun.labels"
    # datapath = "../testdata/fun.data"
    # ds = AnnotatedDataset.parse_sentence(labelspath, datapath)
    # ds = AnnotatedDataset.parse_abbadingoformat("../testdata/train170.txt")
    # ds = AnnotatedDataset.parse_ewsformat_bin(labelspath, datapath)
    ds = Dataset.parse_linewise("testdata/KtestableDataSample.txt")
    # labelspath = "../testdata/lol.labels"
    # datapath = "../testdata/lol.data"
    # ds = Dataset.parse_sentence(datapath)
    ds = Dataset.from_list(["abracadabra"])
    dfa = build_ktestable_DFA(2, ds)
    for sample in ds:
        if dfa.membership(sample[0]) != Result.accept:
            print "problem", sample[0]
    # dfa.write_graphviz('test.txt')
    #dfa = dfa.minimize().rename()
    #dfa.del_dead_states()

    dfa.write_png()
    print dfa
    # for i in dfa.delta:
    #    print i


if __name__ == '__main__':

    cProfile.run('run()')
    # run()
