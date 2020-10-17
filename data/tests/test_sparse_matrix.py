'''
Created on 04.03.2013

@author: hlampesberger
'''
import unittest
import copy
from data.sparse_matrix import SparseStateMatrix

class TestSparseStructures(unittest.TestCase):
    def setUp(self):
        self.sp0 = SparseStateMatrix()
        self.sp1 = SparseStateMatrix()
        self.states = set(range(8))
        self.transitions = [(0, 0, 0), (0, 1, 0),
               (1, 0, 2), (1, 1, 5),
               (2, 0, 3), (2, 1, 7),
               (3, 0, 3), (3, 1, 4),
               (4, 0, 3), (4, 1, 7),
               (5, 0, 6), (5, 1, 7),
               (6, 0, 7), (6, 1, 5),
               (7, 0, 7), (7, 1, 7), ]
        for s, sym, ns in self.transitions:
            if sym == 0:
                self.sp0[s, ns] = True
            elif sym == 1:
                self.sp1[s, ns] = True


    def test_validity(self):
        for i in self.sp0:
            tpl = (i[0], 0, i[1])
            self.assertTrue(tpl in self.transitions)
        for i in self.sp1:
            tpl = (i[0], 1, i[1])
            self.assertTrue(tpl in self.transitions)
        self.assertTrue(self.sp0.is_complete(self.states))
        self.assertTrue(self.sp1.is_complete(self.states))
        self.assertTrue(self.sp0.is_deterministic())
        self.assertTrue(self.sp1.is_deterministic())



    def test_completeness_determinism(self):
        self.assertFalse(self.sp0.transpose().is_deterministic())
        cp = copy.copy(self.sp0)
        self.assertTrue(cp.is_complete(self.states))
        del(cp[0, 0])
        self.assertFalse(cp[0, 0])
        self.assertFalse(cp.is_complete(self.states))


    def test_transition(self):
        state = {1}
        state = self.sp0.transition(state)
        state = self.sp0.transition(state)
        self.assertEqual(state, {3})

    def test_det_transition(self):
        assert(self.sp0.is_deterministic())
        state = 1
        state = self.sp0.det_transition(state)
        state = self.sp0.det_transition(state)
        self.assertEqual(state, 3)

    def test_successor_predecessor(self):
        self.assertEqual(self.sp0.successors(3), {3})
        self.assertEqual(self.sp0.successors({3, 5, 6}), {3, 6, 7})
        self.assertEqual(self.sp0.predecessors(3), {2, 3, 4})


    def test_nondeterminism(self):
        cp = copy.copy(self.sp0)
        cp[1, 5] = True
        # cp[2,1] = True
        state = {1}
        state = cp.transition(state)
        # print state
        state = cp.transition(state)
        # print state
        state = cp.transition(state)
        # print state
        state = cp.transition(state)
        # print state
        state = cp.transition(state)
        self.assertEqual(state, {3, 7})



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
