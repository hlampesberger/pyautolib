'''
Created on 04.03.2013

@author: hlampesberger
'''
import unittest
from data.dataset import AnnotatedDataset
from data.otable import ObservationTable

class TestObservationTable(unittest.TestCase):
    def setUp(self):
        self.raw = [("bb", 1), ("abb", 1), ("bba", 1), ("bbb", 1),
                    ("a", 0), ("b", 0), ("aa", 0), ("bab", 0)]
        self.ds = AnnotatedDataset.from_tuples(self.raw)


    def test_constr(self):
        ot = ObservationTable(self.ds.alphabet, self.ds)
        # ot.print_table()
        self.assertEqual(ot(tuple(""), tuple("")), None)
        self.assertEqual(ot(tuple(""), tuple("a")), 0)
        self.assertEqual(ot(tuple(""), tuple("b")), 0)
        self.assertEqual(ot(tuple(""), tuple("aa")), 0)
        self.assertEqual(ot(tuple(""), tuple("ab")), None)
        self.assertEqual(ot(tuple(""), tuple("ba")), None)
        self.assertEqual(ot(tuple(""), tuple("bb")), 1)
        self.assertEqual(ot(tuple(""), tuple("abb")), 1)
        self.assertEqual(ot(tuple(""), tuple("bab")), 0)
        self.assertEqual(ot(tuple(""), tuple("bba")), 1)
        self.assertEqual(ot(tuple(""), tuple("bbb")), 1)

        self.assertEqual(ot(tuple("a"), tuple("")), 0)
        self.assertEqual(ot(tuple("a"), tuple("a")), 0)
        self.assertEqual(ot(tuple("a"), tuple("b")), None)
        self.assertEqual(ot(tuple("a"), tuple("bb")), 1)

        self.assertEqual(ot(tuple("b"), tuple("")), 0)
        self.assertEqual(ot(tuple("b"), tuple("b")), 1)
        self.assertEqual(ot(tuple("b"), tuple("ab")), 0)
        self.assertEqual(ot(tuple("b"), tuple("ba")), 1)
        self.assertEqual(ot(tuple("b"), tuple("bb")), 1)

        self.assertTrue(ot.states_compatible(tuple("a"), tuple()))
        self.assertFalse(ot.states_compatible(tuple(), tuple("b")))

    def test_promote(self):
        ot = ObservationTable(self.ds.alphabet, self.ds)
        ot.promote_state(tuple("b"))
        self.assertEqual(ot.red_set, set([tuple(), ('b',)]))
        self.assertEqual(ot.blue_set, set([('b', 'a'), ('a',), ('b', 'b')]))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
