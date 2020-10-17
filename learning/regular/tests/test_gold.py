'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from data.dataset import AnnotatedDataset
from learning.regular.gold import build_gold_DFA
import unittest


class TestGold(unittest.TestCase):
    def setUp(self):
        self.raw = [("bb", 1), ("abb", 1), ("bba", 1), ("bbb", 1),
                    ("a", 0), ("b", 0), ("aa", 0), ("bab", 0)]
        self.ds = AnnotatedDataset.from_tuples(self.raw)

    def test_build_gold_DFA(self):
        dfa = build_gold_DFA(self.ds)
        # dfa.write_graphviz("test.txt")
        for s in self.ds.filter(1):
            self.assertEqual(dfa.membership(s[0]), Result.accept)
        for s in self.ds.filter(0):
            if s != (['a', 'a'], 0):
                self.assertEqual(dfa.membership(s[0]), Result.reject)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
