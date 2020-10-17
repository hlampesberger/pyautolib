'''
Created on 04.03.2013

@author: hlampesberger
'''
import unittest
from base import Result
from data.dataset import AnnotatedDataset
from learning.regular.edsm import build_edsm_DFA, _edsm_count
from learning.regular.pta import build_PTA

class TestEDSM(unittest.TestCase):
    def setUp(self):
        self.raw = [("aaa", 1), ("aaba", 1), ("bba", 1), ("bbaba", 1),
                    ("a", 0), ("bb", 0), ("aab", 0), ("aba", 0)]
        self.ds = AnnotatedDataset.from_tuples(self.raw)

    def test_edsm_count(self):
        ppta = build_PTA(self.ds)
        score = _edsm_count(ppta, self.ds)
        self.assertEqual(score, 0.0)

    def test_build_edsm_DFA(self):
        dfa = build_edsm_DFA(self.ds)
#        dfa.write_graphviz("test.txt")
        for s in self.ds.filter(1):
            self.assertEqual(dfa.membership(s[0]), Result.accept)
        for s in self.ds.filter(0):
            self.assertEqual(dfa.membership(s[0]), Result.reject)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
