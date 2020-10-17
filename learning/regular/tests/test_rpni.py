'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from data.dataset import AnnotatedDataset
from learning.regular.rpni import build_rpni_DFA
import unittest


class TestRPNI(unittest.TestCase):
    def setUp(self):
        self.raw = [("aaa", 1), ("aaba", 1), ("bba", 1), ("bbaba", 1),
                    ("a", 0), ("bb", 0), ("aab", 0), ("aba", 0)]
        self.ds = AnnotatedDataset.from_tuples(self.raw)

    def test_build_rpni_DFA(self):
        dfa = build_rpni_DFA(self.ds)
        # write_graphviz(dfa, "test.txt")
        for s in self.ds.filter(1):
            self.assertEqual(dfa.membership(s[0]), Result.accept)
        for s in self.ds.filter(0):
            self.assertEqual(dfa.membership(s[0]), Result.reject)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
