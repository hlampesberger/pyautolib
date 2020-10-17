'''
Created on 16.04.2013

@author: hlampesberger
'''
from data.corpus import Corpus, AnnotatedCorpus
import os.path
import unittest


class TestCorpus(unittest.TestCase):
    def test_path(self):
        c = Corpus.from_path(".")
        for path in c:
            self.assertTrue(os.path.isfile(path))


class TestAnnotatedCorpus(unittest.TestCase):
    def test_path(self):
        c = AnnotatedCorpus.from_path(".", {"": 0, "s" : 1})
        for path, _ in c:
            self.assertTrue(os.path.isfile(path))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
