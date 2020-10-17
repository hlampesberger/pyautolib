'''
Created on 16.04.2013

@author: hlampesberger
'''
import time


class BinaryClassificationPerformance(object):
    def __init__(self):
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.duration = None

    def add(self, truth, result):
        if result:
            if truth:
                self.tp += 1
            else:
                self.fp += 1
        else:
            if truth:
                self.fn += 1
            else:
                self.tn += 1

    def start(self):
        self.duration = time.time()

    def stop(self):
        self.duration = time.time() - self.duration

    def total(self):
        return self.tp + self.fp + self.tn + self.fn

    def precision(self):
        if self.tp > 0 or self.fp > 0:
            return float(self.tp) / (self.tp + self.fp)
        return 0.0

    def recall(self):
        if self.tp > 0 or self.fn > 0:
            return float(self.tp) / (self.tp + self.fn)
        return 0.0
    tpr = recall

    def accuracy(self):
        if self.total() > 0:
            return float(self.tp + self.tn) / \
                   (self.tp + self.tn + self.fp + self.fn)
        return 0.0

    def tnr(self):
        if self.tn > 0 or self.fp > 0:
            return float(self.tn) / (self.tn + self.fp)
        return 0.0

    def tpr(self):
        return self.recall()


    def fpr(self):
        if self.fp > 0 or self.tn > 0:
            return float(self.fp) / (self.fp + self.tn)
        return 0.0

    def fnr(self):
        if self.tp > 0 or self.fn > 0:
            return float(self.fn) / (self.tp + self.fn)
        return 0.0

    def f_beta_measure(self, beta):
        rc = self.recall()
        pr = self.precision()
        if rc > 0 or pr > 0:
            return (1 + beta) * pr * rc / (beta * pr + rc)
        else:
            return 0.0

    def f_measure(self):
        return self.f_beta_measure(1)


    def __str__(self):
        return "tp:%d fp:%d tn:%d fn:%d rc:%f pr:%f F:%f acc:%f fpr:%f tnr:%f dur:%s" % \
                (self.tp, self.fp, self.tn, self.fn, self.recall(),
                 self.precision(), self.f_measure(), self.accuracy(),
                 self.fpr(), self.tnr(), str(self.duration))
