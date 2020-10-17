'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from data.dataset import AnnotatedDataset, Dataset
from learning.regular.pta import build_PTA
import unittest


class TestPTA(unittest.TestCase):
    def setUp(self):
        self.raw = [("aa", 1), ("aba", 1), ("bba", 1), ("ab", 1), ("abab", 1)]
        self.ds = AnnotatedDataset.from_tuples(self.raw)
        self.bds = Dataset.from_list(map(lambda x: x[0], self.raw))

    def test_PTA(self):
        pta = build_PTA(self.ds)
        pta2 = build_PTA(self.bds)
        for i in self.raw:
            self.assertEqual(pta2.membership(i[0]), Result.accept)
            if i[1] == 1:
                self.assertEqual(pta.membership(i[0]), Result.accept)
            else:
                self.assertEqual(pta.membership(i[0]), Result.reject)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
