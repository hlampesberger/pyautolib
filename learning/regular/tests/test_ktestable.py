'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from data.dataset import Dataset
from learning.regular.ktestable import build_ktestable_DFA, _build_TSS_machine
import unittest



class TestTSS(unittest.TestCase):
    def setUp(self):
        self.raw = ["a", "aa", "abba", "abbbba"]
        self.ds = Dataset.from_list(self.raw)


    def test_ktestable_DFA(self):
        tss_dfa = build_ktestable_DFA(2, self.ds)
        # tss_dfa.write_graphviz("test.txt")
        for i in self.raw:
            self.assertEqual(tss_dfa.membership(i), Result.accept)

    def test_build_TSS_machine(self):
        tss = _build_TSS_machine(3, self.ds)
        self.assertEqual(tss[0], set(map(tuple, ["aa", "ab"])))
        # self.assertEqual(tss[1], set(["a", "aa"]))
        self.assertEqual(tss[1], set(map(tuple, ["aa", "ba"])))
        self.assertEqual(tss[2], set(map(tuple, ["abb", "bbb", "bba"])))
        self.assertEqual(tss[3], set(map(tuple, ["a", "aa"])))



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
