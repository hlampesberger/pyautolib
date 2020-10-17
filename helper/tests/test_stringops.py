'''
Created on 04.03.2013

@author: hlampesberger
'''

from helper.stringops import prefixes, suffixes, prefix_symbol_suffix
import unittest

class TestStringOps(unittest.TestCase):
    def test_prefixes(self):
        strng = list("abcdefg")
        for i in prefixes(strng):
            self.assertTrue(''.join(i) in ''.join(strng))

    def test_suffixes(self):
        strng = list("abcdefg")
        for i in suffixes(strng):
            self.assertTrue(''.join(i) in ''.join(strng))

    def test_prefix_symbol_suffix(self):
        strng = list("abcdefg")
        for prefix, symbol, suffix in prefix_symbol_suffix(strng):
            self.assertEqual(prefix + symbol + suffix, strng)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
