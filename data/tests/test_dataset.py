'''
Created on 04.03.2013

@author: hlampesberger
'''
import unittest

from data.dataset import Dataset, AnnotatedDataset

class TestDataset(unittest.TestCase):

    def test_BasicDataset(self):
        path = "pyautomata/testdata/cms.01.data"
        ds = Dataset.parse_linewise(path)
        self.assertTrue(ds[2])
        self.assertEqual(len(ds), 3279)
        lst = ["a", "abc"]
        ds = Dataset.from_list(lst)
        self.assertTrue((["a"],) in ds)

    def test_AnnotatedDataset(self):
        labelspath = "pyautomata/testdata/cms.01.labels"
        datapath = "pyautomata/testdata/cms.01.data"
        ds = AnnotatedDataset.parse_ewsformat(labelspath, datapath)
        # print ds.alphabet
        self.assertTrue(ds[3])
        self.assertEqual(len(ds), 3279)
        self.assertEqual(len(ds.labels), 9)
        ds = AnnotatedDataset.parse_ewsformat_bin(labelspath, datapath)
        self.assertTrue(ds[3])
        self.assertEqual(len(ds), 3279)
        self.assertEqual(len(ds.labels), 2)


    def test_abbadingo(self):
        datapath = "pyautomata/testdata/train170.txt"
        # datapath = "../../testdata/train170.txt"
        ds = AnnotatedDataset.parse_abbadingoformat(datapath)
        self.assertEqual(len(ds), 3000)
        self.assertEqual(len(ds[6][0]), 14)
        self.assertTrue(ds[6] in ds)
        self.assertEqual(len(ds), len(ds.filter(0)) + len(ds.filter(1)))


    def test_from_tuples(self):
        examples = [("abc", 1), ("ade", 0), ("xc", 1)]
        ds = AnnotatedDataset.from_tuples(examples)
        self.assertEqual(ds.alphabet, set("abcdex"))
        self.assertEqual(ds.labels, {1, 0})

    def test_from_list(self):
        examples = ["abc", "ade", "xc"]
        ds = Dataset.from_list(examples)
        self.assertEqual(ds.alphabet, set("abcdex"))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
