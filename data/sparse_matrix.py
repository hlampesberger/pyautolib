# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 16:27:31 2012

@author: hlampesberger
"""



__all__ = ['SparseStateMatrix']


class SparseStateMatrix(object):
    def __init__(self, pairs=[]):
        self.data = dict()
        for s, ns in pairs:
            self[s, ns] = True


    def __setitem__(self, key, value):
        # key is a tuple state x next_state, value is some value
        if not value:
            del(self[key])
        else:
            row, col = key
            if row not in self.data:
                self.data[row] = [col]
            else:
                if col not in self.data[row]:
                    self.data[row].append(col)


    def __getitem__(self, key):
        row, col = key
        if row in self.data:
            return col in self.data[row]
        else:
            return False

    def __delitem__(self, key):
        row, col = key
        if row in self.data:
            if col in self.data[row]:
                self.data[row].remove(col)
            if not self.data[row]:
                del(self.data[row])

    def __iter__(self):
        for x, tmp in self.data.items():
            for y in tmp:
                yield x, y

    def __copy__(self):
        return SparseStateMatrix(iter(self))

    def __repr__(self):
        return "SparseStateMatrix(%s)" % \
        [(x, y) for x, tmp in self.data.items() for y in tmp ]

    def transpose(self):
        fresh = SparseStateMatrix()
        for x, y in self:
            fresh[y, x] = True
        return fresh

    def is_complete(self, state_set):
        if state_set == set(self.data.keys()):
            for x, tmp in self.data.items():
                if not {s for s in tmp if s in state_set}:
                    return False
            return True
        else:
            return False

    def is_deterministic(self):
        for x, tmp in self.data.items():
            if len(tmp) > 1:
                return False
        return True


    def predecessors(self, state):
        if isinstance(state, set):
            return { s for s, ns in self.data.items() if set(ns) & state }
        else:
            # single state
            return { s for s, ns in self.data.items() if state in ns }

    def successors(self, state):
        if isinstance(state, set):
            return { ns for s in state if s in self.data for ns in self.data[s] }
        else:
            if state in self.data:
                return set(self.data[state])
            else:
                return set()


    def det_transition(self, state):
        # no further checks done for performance
        if state in self.data:
            return self.data[state][0]


    def transition(self, state_set):
        return self.successors(state_set)


    def del_state(self, state):
        if state in self.data:
            del(self.data[state])
        k = self.data.keys()
        for x in k:
            del(self[x, state])

    def update(self, other):
        # keys must not overlap!
        self.data.update(other.data)

    def set_error_state(self, state_set, err_state):
        for s in state_set:
            if s in self.data:
                if not self.data[s]:
                    self[s, err_state] = True
            else:
                self[s, err_state] = True


    copy = __copy__


