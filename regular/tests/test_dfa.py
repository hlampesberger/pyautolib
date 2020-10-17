'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from regular import nfa
from regular.dfa import DFA
import unittest



class TestDFA(unittest.TestCase):

    def setUp(self):
        alphabet = ["a", "b"]
        s = ["q1", "q2", "q3", "q4"]
        transitions = [("q1", "b", "q1"), ("q1", "a", "q2"),
                       ("q2", "a", "q3"), ("q2", "b", "q4"),
                       ("q3", "a", "q4"), ("q3", "b", "q3"),
                       ("q4", "a", "q2"), ("q4", "b", "q1")]
        acc_s = ["q2", "q3"]
        rej_s = ["q4"]
        self.fsa = DFA.build(alphabet=alphabet, states=s,
                             start_state="q1",
                             accept_states=acc_s,
                             reject_states=rej_s,
                             transitions=transitions)



    def test_DFA_membership(self):
        self.assertEqual(self.fsa.membership(""), Result.neutral)
        self.assertEqual(self.fsa.membership("a"), Result.accept)
        self.assertEqual(self.fsa.membership("ab"), Result.reject)
        self.assertEqual(self.fsa.membership("abb"), Result.neutral)
        self.assertEqual(self.fsa.membership("aba"), Result.accept)
        self.assertEqual(self.fsa.membership("abaab"), Result.accept)


    def test_incomplete(self):
        alphabet = ["a", "b"]
        s = [1, 2, 3, 4]
        transitions = [(1, "b", 1), (1, "a", 2),
                       (2, "a", 3), (2, "b", 4)]
        acc_s = [2, 3]
        rej_s = [4]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        self.assertFalse(dfa.is_complete())
        dfa.transitions = None
        dfa.complete(sink=4)
        self.assertTrue(dfa.is_complete())


    def test_del_dead_states(self):
        alphabet = ["a", "b"]
        s = [1, 2, 3, 4]
        transitions = [(1, "b", 1), (1, "a", 2),
                       (2, "a", 3), (2, "b", 4),
                       (3, "a", 4), (3, "b", 3),
                       (4, "a", 2), (4, "b", 1)]
        acc_s = [2, 3]
        rej_s = [4]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        dfa.del_states({4})
        self.assertFalse(dfa.is_complete())
        self.assertEqual(len(set(dfa.itertransitions())), 4)
        dfa.complete(6)
        self.assertTrue(dfa.is_complete())
        self.assertEqual(len(set(dfa.itertransitions())), 8)
        dfa.del_dead_states()
        self.assertTrue(6 not in dfa.states)
        self.assertEqual(len(set(dfa.itertransitions())), 4)
        self.assertFalse(dfa.is_complete())


    def test_del_unreachable_states(self):
        alphabet = ["a", "b"]
        s = [1, 2, 3, 4, 5]
        transitions = [(1, "b", 1), (1, "a", 2),
                       (2, "a", 3), (2, "b", 4),
                       (3, "a", 4), (3, "b", 3),
                       (4, "a", 2), (4, "b", 1),
                       (5, "a", 2), (5, "b", 3)]
        acc_s = [2, 3]
        rej_s = [4, 5, 1]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        self.assertTrue(5 not in dfa.reachable_states())
        self.assertTrue(dfa.is_complete())
        dfa.del_unreachable_states()
        self.assertTrue(dfa.is_complete())


    def test_DFA_numeric_states(self):
        alphabet = ["a", "b"]
        s = [1, 2, 3, 4]
        transitions = [(1, "b", 1), (1, "a", 2),
                       (2, "a", 3), (2, "b", 4),
                       (3, "a", 4), (3, "b", 3),
                       (4, "a", 2), (4, "b", 1)]
        acc_s = [2, 3]
        rej_s = [4]
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                        accept_states=acc_s, reject_states=rej_s,
                        transitions=transitions)
        self.assertEqual(dfa.membership(""), Result.neutral)
        self.assertEqual(dfa.membership("a"), Result.accept)
        self.assertEqual(dfa.membership("ab"), Result.reject)
        self.assertEqual(dfa.membership("abb"), Result.neutral)
        self.assertEqual(dfa.membership("aba"), Result.accept)
        self.assertEqual(dfa.membership("abaab"), Result.accept)


    def test_union_intersection_subset(self):
        alphabet = [0, 1]
        s = ["A", "B"]
        transitions = [("A", 0, "A"), ("A", 1, "B"),
                       ("B", 0, "A"), ("B", 1, "A")]
        acc_s = ["B"]
        rej_s = ["A"]
        dfa1 = DFA.build(alphabet=alphabet, states=s, start_state="A",
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        s = ["C", "D"]
        transitions = [("C", 0, "D"), ("C", 1, "C"),
                       ("D", 0, "D"), ("D", 1, "C")]
        acc_s = ["C"]
        rej_s = ["D"]
        dfa2 = DFA.build(alphabet=alphabet, states=s, start_state="D",
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        udfa = dfa1 | dfa2
        idfa = dfa1 & dfa2
        self.assertEqual(idfa.membership([0, 1]), Result.accept)
        self.assertEqual(idfa.membership([1]), Result.accept)
        self.assertEqual(dfa1.membership([0, 1, 1]), Result.reject)
        self.assertEqual(udfa.membership([0, 1, 1]), Result.accept)
        self.assertTrue(dfa1.issubset(dfa2))

    def test_equality(self):
        alphabet = [0, 1]
        s = ["A", "B"]
        # lang: 0, 01, 011, 0111, ... = 01*
        transitions = [("A", 0, "B"), ("B", 1, "B")]
        acc_s = ["B"]
        rej_s = ["A"]
        dfa1 = DFA.build(alphabet=alphabet, states=s, start_state="A",
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        s = ["X", "Y", "Z"]
        transitions = [("X", 0, "Y"), ("Y", 1, "Z"), ("Z", 1, "Z")]
        acc_s = ["Y", "Z"]
        rej_s = ["X"]
        dfa2 = DFA.build(alphabet=alphabet, states=s, start_state="X",
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)

        # test incompleteness
        self.assertEqual(dfa1.membership([1, 1, 1]), Result.reject)

        dfa1.complete()
        dfa2.complete()
        self.assertTrue(dfa1 == dfa2)
        
        # test equivalence pairs
        eq_pairs = {('A', 'X'), ('B', 'Y'), ('B', 'Z'), (-1, -1)}
        self.assertEqual(dfa1.equivalent_states(dfa2), eq_pairs)
        
        udfa = dfa1 | dfa2
        self.assertEqual(udfa.membership([0]), Result.accept)
        self.assertEqual(udfa.membership([1]), Result.reject)
        self.assertEqual(udfa.membership([0, 1]), Result.accept)
        self.assertEqual(udfa.membership([0, 1, 1]), Result.accept)
        self.assertEqual(udfa.membership([0, 0, 0]), Result.reject)
        self.assertEqual(udfa.membership([0, 1, 1, 1, 1, 1]), Result.accept)


    def test_minimize(self):
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
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        mindfa = dfa.minimize()
        # quick'n'dirty test whether automaton is equivalent
        brzozowski = nfa.NFA.viewDFA(dfa).reverse().determinize()
        brzozowski = nfa.NFA.viewDFA(brzozowski).reverse().determinize()
        self.assertTrue(mindfa == dfa)
        self.assertTrue(brzozowski == mindfa)
        self.assertEqual(mindfa.membership("ab"), Result.accept)
        self.assertEqual(mindfa.membership("bb"), Result.accept)
        self.assertEqual(mindfa.membership("baa"), Result.accept)
        self.assertEqual(mindfa.membership("aabb"), Result.accept)
        self.assertEqual(mindfa.membership("aaaaaaaaaabbbbb"), Result.accept)


    def test_reversal(self):
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
        dfa = DFA.build(alphabet=alphabet, states=s, start_state=1,
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        rev = dfa.reverse()
        self.assertEqual(rev.membership("ba"), Result.accept)
        self.assertEqual(rev.membership("aaaaaabb"), Result.accept)
        self.assertEqual(rev.membership("ab"), Result.reject)
        self.assertEqual(rev.membership("aba"), Result.accept)
        self.assertEqual(rev.membership("abaab"), Result.accept)


    def test_concat(self):
        alphabet = [0, 1]
        s = ["A", "B"]
        # lang: 0, 01, 011, 0111, ... = 01*
        transitions = [("A", 0, "B"), ("B", 1, "B")]
        acc_s = ["B"]
        rej_s = ["A"]
        dfa1 = DFA.build(alphabet=alphabet, states=s, start_state="A",
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        s = ["X", "Y", "Z"]
        transitions = [("X", 0, "Y"), ("Y", 1, "Z"), ("Z", 1, "Z")]
        acc_s = ["Y", "Z"]
        rej_s = ["X"]
        dfa2 = DFA.build(alphabet=alphabet, states=s, start_state="X",
                         accept_states=acc_s, reject_states=rej_s,
                         transitions=transitions)
        dfa3 = (dfa1 * dfa2).minimize().rename()
        # dfa3 is 01*01*,
        self.assertEqual(dfa3.membership([1]), Result.reject)
        self.assertEqual(dfa3.membership([0, 0]), Result.accept)
        self.assertEqual(dfa3.membership([0, 1, 0]), Result.accept)
        self.assertEqual(dfa3.membership([0, 0, 0]), Result.reject)
        self.assertEqual(dfa3.membership([0, 1, 1]), Result.reject)
        self.assertEqual(dfa3.membership([0, 1, 1, 1, 1, 1]), Result.reject)





if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
