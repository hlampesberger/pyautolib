'''
Created on 04.03.2013

@author: hlampesberger
'''
from learning.regular.lstar import build_lstar_DFA
from regular.dfa import DFA
from regular.oracle import MinAdequateTeacher
import unittest


class TestLSTAR(unittest.TestCase):
    def setUp(self):
        a = "a"
        b = "b"
        alphabet = [a, b]
        s = [0, 1, 2, 3, 4, 5, 6]
        transitions = [(0, a, 0), (0, b, 0),
                       (1, a, 2), (1, b, 5),
                       (2, a, 3), (2, b, 0),
                       (3, a, 3), (3, b, 4),
                       (4, a, 3), (4, b, 0),
                       (5, a, 6), (5, b, 0),
                       (6, a, 0), (6, b, 5)]
        acc_s = [0, 5]
        rej_s = [1, 2, 3, 4, 6]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        self.dfa2 = dfa.minimize()
        # self.dfa2.write_graphviz("target.txt")
        self.mat = MinAdequateTeacher(dfa)

    def test_init(self):
        dfa = build_lstar_DFA(self.mat)
        self.assertTrue(dfa == self.dfa2)
        dfa.write_png()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
