'''
Created on 16.04.2013

@author: hlampesberger
'''

import os
import os.path

__all__ = ['Corpus', 'AnnotatedCorpus']

class Corpus(list):
    def __repr__(self):
        return "<%s size:%d>" % (self.__class__.__name__, len(self))

    @staticmethod
    def from_path(dirpath):
        return Corpus([os.path.join(dirpath, f) for f in os.listdir(dirpath) \
                       if os.path.isfile(os.path.join(dirpath, f))])



class AnnotatedCorpus(Corpus):
    def __init__(self, labels, *args):
        assert(isinstance(labels, set))
        self.labels = labels
        super(AnnotatedCorpus, self).__init__(*args)

    def filter(self, label):
        assert(label in self.labels)
        for x in self:
            if x[1] == label:
                yield x[0]
#        return Corpus(x[0] for x in self if x[1] == label)

    @staticmethod
    def from_path(dirpath, prefix_dict):
        def lab(fname):
            for pref, label in prefix_dict.items():
                if fname.startswith(pref):
                    return label
            raise RuntimeError("invalid filename prefix")
        return AnnotatedCorpus(set(prefix_dict.values()),
                               [(os.path.join(dirpath, f), lab(f)) for f in os.listdir(dirpath) \
                                if os.path.isfile(os.path.join(dirpath, f))])
