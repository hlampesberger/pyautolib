'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result, epsilon
from regular.nfa import NFA
import itertools
import unittest


class TestNFA(unittest.TestCase):

    def test_NFA_reversal(self):
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
        rej_s = [1, 2, 4, 6]
        nfa = NFA.build(alphabet=alphabet, states=s, start_states={1},
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        rev = nfa.reverse()
        # equivalence of undefined states
        self.assertEqual(nfa.states - nfa.accept - nfa.reject,
                         rev.states - rev.accept - rev.reject)
        self.assertEqual(rev.membership("ba"), Result.accept)
        self.assertEqual(rev.membership("aaaaaabb"), Result.accept)
        self.assertEqual(rev.membership("ab"), Result.reject)
        self.assertEqual(rev.membership("aba"), Result.accept)
        self.assertEqual(rev.membership("abaab"), Result.accept)


    def test_determinization1(self):
        alphabet = [0, 1]
        s = ["q0", "q1", "q2"]
        start = ["q0"]
        acc = ["q2"]
        rej = ["q0", "q1"]
        t = [("q0", 0, "q0"), ("q0", 1, "q0"), ("q0", 0, "q1"),
             ("q1", 1, "q2")]
        orignfa = NFA.build(alphabet=alphabet, states=s, start_states=start,
                        accept_states=acc, reject_states=rej,
                        transitions=t)
        convdfa = orignfa.determinize()
        self.assertEqual(orignfa.membership([0, 1, 0, 1]), Result.accept)
        self.assertEqual(convdfa.membership([0, 1, 0, 1]), Result.accept)



    def test_determinization2(self):
        alphabet = ["r", "b"]
        s = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        transitions = [(1, "r", 2), (1, "r", 4), (1, "b", 5),
                       (2, "r", 4), (2, "r", 6), (2, "b", 1), (2, "b", 3),
                       (2, "b", 5),
                       (3, "r", 2), (3, "r", 6), (3, "b", 5),
                       (4, "r", 2), (4, "r", 8), (4, "b", 1), (4, "b", 5),
                       (4, "b", 7),
                       (5, "r", 2), (5, "r", 4), (5, "r", 6), (5, "r", 8),
                       (5, "b", 1), (5, "b", 3), (5, "b", 7), (5, "b", 9),
                       (6, "r", 2), (6, "r", 8), (6, "b", 3), (6, "b", 5),
                       (6, "b", 9),
                       (7, "r", 4), (7, "r", 8), (7, "b", 5),
                       (8, "r", 4), (8, "r", 6), (8, "b", 5), (8, "b", 7),
                       (8, "b", 9),
                       (9, "r", 6), (9, "r", 8), (9, "b", 5),
                       (1, epsilon, 2), (7, epsilon, 8), (9, epsilon, 7)
                       ]
        acc_s = [9]
        start = [1]
        rej_s = [1, 2, 3, 4]

        orignfa = NFA.build(alphabet=alphabet, states=s, start_states=start,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        # orignfa.write_png("test.png")
        convdfa = orignfa.determinize()
        # convdfa.write_png("test1.png")
        for i in xrange(4):
            for sample in itertools.permutations("r" * i + "b" * i):
                s = ''.join(sample)
                # print s, ":", orignfa.membership(s), convdfa.membership(s)
                self.assertEqual(orignfa.membership(s),
                                 convdfa.membership(s))


    def test_NFA_membership(self):
        alphabet = [0, 1]
        s = ["A", "B", "C"]
        transitions = [("A", 0, "A"), ("A", 1, "B"),
                       ("B", 0, "A"), ("B", 0, "C"),
                       ("C", 1, "B"), ("C", 1, "A")]
        acc_s = ["C"]
        rej_s = ["A", "B"]
        start = ["A"]
        tests = [((0, 0, 1, 1, 0, 1, 0, 0), Result.reject),
                 ((0, 1, 0, 1, 0, 0, 1, 1), Result.reject),
                 ((0, 1, 0, 1, 1, 1), Result.reject),
                 ((1, 0, 0, 0, 1, 0, 1, 0), Result.accept)]
        nfa = NFA.build(alphabet=alphabet, states=s, start_states=start,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        self.assertTrue(nfa.is_epsilon_free())
        dfa = nfa.determinize().minimize()
        for t in tests:
            self.assertEqual(nfa.membership(t[0]), t[1])
            self.assertEqual(dfa.membership(t[0]), t[1])





if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
