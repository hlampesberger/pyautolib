# -*- coding: utf-8 -*-
"""
Created on Mon May 21 12:37:22 2012

@author: hlampesberger
"""

import collections

__all__ = ['Dataset', 'AnnotatedDataset']


def _parse_abbadingo(strng):
    lst = strng.rstrip('\r\n').split(' ')
    return map(int, lst[2:]), int(lst[0])


class Dataset(object):
    def __init__(self, alphabet, data):
        self.alphabet = alphabet
        self.dataset = data

    def __in__(self, item):
        return item in self.dataset

    def __len__(self):
        return len(self.dataset)

    def __iter__(self):
        return iter(self.dataset)

    def __getitem__(self, ind):
        return self.dataset[ind]

    def __repr__(self):
        return "<Dataset len:%d>" % len(self)

    @staticmethod
    def from_list(lst):
        # data = map(lambda x: (list(x),), lst)
        data = [(list(x),) for x in lst]
        alphabet = {x for d in data for x in d[0]}
        # alphabet = reduce(lambda s, x: s.union(set(x[0])), data, set())
        return Dataset(alphabet, data)

    @staticmethod
    def parse_linewise(path):
        with open(path, "r") as f:
            # data = map(lambda s: (list(s.rstrip('\r\n')),), f.readlines())
            data = [(list(s.rstrip('\r\n')),) for s in f.readlines()]
            alphabet = {x for d in data for x in d[0]}
            # alphabet = reduce(lambda s, x: s.union(set(x[0])), data, set())
            return Dataset(alphabet, data)

    @staticmethod
    def parse_sentence(path):
        with open(path, "r") as f:
#            data = map(lambda s: (s.rstrip('\r\n').split(),), f.readlines())
            data = [(s.rstrip('\r\n').split(),) for s in f.readlines()]
            alphabet = {x for d in data for x in d[0]}
#            alphabet = set(reduce(lambda s, x: s.union(x[0]), data, set()))
            return Dataset(alphabet, data)




class AnnotatedDataset(Dataset):
    def __init__(self, alphabet, labelset, data):
        self.labels = set(labelset)
        super(AnnotatedDataset, self).__init__(alphabet, data)

    def __repr__(self):
        return "<AnnotatedDataset len:%d types:%d>" % (len(self),
                                                       len(self.labels))

    def filter(self, label):
        return AnnotatedDataset(self.alphabet, set([label]),
                                filter(lambda x: x[1] == label,
                                       self.dataset))

    @staticmethod
    def from_tuples(lst):
        data = [(list(x[0]), x[1]) for x in lst]
        alphabet = {x for d in data for x in d[0]}
        labels = {d[1] for d in data}
        return AnnotatedDataset(alphabet, labels, data)

    @staticmethod
    def parse_ewsformat(labelpath, datapath):
        labelref = collections.defaultdict(lambda: 0)
        with open(labelpath, "r") as f:
            for line in f.readlines():
                (linenr, tag) = line.rstrip('\r\n').split(':')
                labelref[int(linenr)] = int(tag)
        with open(datapath, "r") as f:
            data = [(list(s.rstrip('\r\n')), labelref[i + 1]) for i, s in enumerate(f.readlines())]
            alphabet = {x for d in data for x in d[0]}
            return AnnotatedDataset(alphabet, set(labelref.values()), data)

    @staticmethod
    def parse_ewsformat_bin(labelpath, datapath):
        labelref = collections.defaultdict(lambda: 0)
        with open(labelpath, "r") as f:
            for line in f.readlines():
                (linenr, tag) = line.rstrip('\r\n').split(':')
                labelref[int(linenr)] = int(tag)

        with open(datapath, "r") as f:
            data = [(list(s.rstrip('\r\n')), int(i + 1 not in labelref)) for i, s in enumerate(f.readlines())]
            alphabet = {x for d in data for x in d[0]}
            return AnnotatedDataset(alphabet, set([0, 1]), data)

    @staticmethod
    def parse_sentence(labelpath, datapath):
        labelref = collections.defaultdict(lambda: 0)
        with open(labelpath, "r") as f:
            for line in f.readlines():
                (linenr, tag) = line.rstrip('\r\n').split(':')
                labelref[int(linenr)] = int(tag)

        with open(datapath, "r") as f:
            data = [(s.rstrip('\r\n').split(), int(i + 1 not in labelref)) for i, s in enumerate(f.readlines())]
            alphabet = {x for d in data for x in d[0]}
            return AnnotatedDataset(alphabet, set([0, 1]), data)
        
    @staticmethod
    def parse_custom(datapath):
        with open(datapath, "r") as f:
            data = []
            for line in f:
                (tag, strng) = line.rstrip('\r\n').split(' ')
                data.append( (strng, int(tag)) )
            alphabet = {x for d in data for x in d[0]}
            return AnnotatedDataset(alphabet, set([0, 1]), data)

    @staticmethod
    def parse_abbadingoformat(path):
        with open(path, "r") as f:
            data = map(_parse_abbadingo, f.readlines()[1:])
            alphabet = {x for d in data for x in d[0]}
            labels = {d[1] for d in data}
            return AnnotatedDataset(alphabet, labels, data)




