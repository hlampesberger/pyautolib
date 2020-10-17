# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:27:02 2012

@author: hlampesberger
"""

from data.dataset import AnnotatedDataset
from learning.regular.rpni import build_rpni_DFA

import cProfile

def run():
    # labelspath = "../testdata/fun.labels"
    # datapath = "../testdata/fun.data"
    # ds = AnnotatedDataset.parse_sentence(labelspath, datapath)
    ds = AnnotatedDataset.parse_abbadingoformat("../../testdata/train171.txt")
    # ds = AnnotatedDataset.parse_abbadingoformat("../testdata/RPNIAndEDSMDataSample.txt")
    # labelspath = "../testdata/cms.01.labels"
    # datapath = "../testdata/cms.01.data"
    # ds = AnnotatedDataset.parse_ewsformat_bin(labelspath, datapath)
    # labelspath = "../testdata/lol.labels"
    # datapath = "../testdata/lol.data"
    # ds = AnnotatedDataset.parse_sentence(labelspath, datapath)
    dfa = build_rpni_DFA(ds)
    # dfa.write_png()

    print dfa.states, dfa.accept, dfa.reject
    for sample in ds:
        # res, state = dfa.parse_final(sample[0])
        res = dfa.membership(sample[0])
        if res != sample[1]:
            print sample, res
    print dfa


if __name__ == '__main__':
    # run()
    cProfile.run('run()')
