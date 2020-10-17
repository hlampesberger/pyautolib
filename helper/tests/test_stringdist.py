'''
Created on 07.03.2013

@author: hlampesberger
'''
from helper.stringdist import hamming_distance, edit_distance
import unittest



class TestStringDistances(unittest.TestCase):
    def test_distance_hamming(self):
        self.assertEqual(hamming_distance("aaba", "abab"), 3)
        self.assertEqual(hamming_distance("ababababab", "bababababa"), 10)

    def test_edit_distance(self):
        self.assertEqual(edit_distance("lol", "l0l"), 2)
        self.assertEqual(edit_distance("hagendasz", "haselblad"), 10)
        self.assertEqual(edit_distance([1, 2, 2, 1, 2, 2, 3], [2, 1, 1, 2, 2]), 4)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
