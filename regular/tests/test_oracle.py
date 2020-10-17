'''
Created on 04.03.2013

@author: hlampesberger
'''
from regular.dfa import DFA
from regular.oracle import MinAdequateTeacher
import unittest



class TestMAT(unittest.TestCase):
    def setUp(self):
        a = "a"
        b = "b"
        alphabet = [a, b]
        s = [10, 1, 2, 3, 4, 5, 6]
        transitions = [(10, a, 10), (10, b, 10),
                       (1, a, 2), (1, b, 5),
                       (2, a, 3), (2, b, 10),
                       (3, a, 3), (3, b, 4),
                       (4, a, 3), (4, b, 10),
                       (5, a, 6), (5, b, 10),
                       (6, a, 10), (6, b, 5)]
        acc_s = [10, 5]
        rej_s = [1, 2, 3, 4]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        # self.dfa2 = copy.copy(dfa).to_reverse_NFA().to_DFA().to_reverse_NFA().to_DFA()
        self.mat = MinAdequateTeacher(dfa)

    def test_membership(self):
        self.assertTrue(self.mat.membership_query(list("aabb")))

    def test_equivalence(self):
        a = "a"
        b = "b"
        alphabet = [a, b]
        s = [10, 1, 2, 3, 4, 5, 6]
        transitions = [(10, a, 10), (10, b, 10),
                       (1, a, 2), (1, b, 5),
                       (2, a, 3), (2, b, 10),
                       (3, a, 3), (3, b, 4),
                       (4, a, 3), (4, b, 10),
                       (5, a, 6), (5, b, 10),
                       (6, a, 10), (6, b, 5)]
        acc_s = [10, 5]
        rej_s = [1, 2, 3, 4]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        # res = self.mat.equivalence_query(dfa)
        self.assertTrue(self.mat.equivalence_query(dfa)[0])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
