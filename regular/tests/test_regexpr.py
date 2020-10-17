'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from regular import dfa
from regular.regexpr import RegExpr
import unittest



class TestRegExpr(unittest.TestCase):
    def test_simple_regex(self):
        strng = "(a+b)c"
        alp = ["a", "b", "c"]
        st = [0, 1, 2, 3]
        tr = [(0, "a", 1), (0, "b", 1), (0, "c", 3),
               (1, "a", 3), (1, "b", 3), (1, "c", 2),
               (2, "a", 3), (2, "b", 3), (2, "c", 3),
               (3, "a", 3), (3, "b", 3), (3, "c", 3)]
        acc = [2]
        rej = [0, 1, 3]
        working = dfa.DFA.build(alphabet=alp, states=st, transitions=tr,
                                start_state=0, accept_states=acc,
                                reject_states=rej)
        self.assertEqual(working.membership("ac"), Result.accept)
        A = RegExpr(strng).mindfa()
        self.assertEqual(working, A)


    def test_advanced_regex(self):
        for i in xrange(1, 3):
            strng = "a?"*i + "a"*i
            test = "a"*i
            RegExpr(strng).mindfa().membership(test)

    def test_equiv(self):
        a = RegExpr("aa*")
        b = RegExpr("a+", syntax="regex")
        self.assertEqual(a.mindfa(), b.mindfa())

    def test_whitespace(self):
        a = RegExpr("(abc + cde*) xyz", whitespace=True)
        A = a.mindfa()
        self.assertEqual(A.membership(['abc', 'xyz']), Result.accept)
        self.assertEqual(A.membership(['xyz']), Result.accept)
        self.assertEqual(A.membership(['xyz', 'xyz']), Result.reject)
        b = RegExpr("(True + False)* True (True + False)*", whitespace=True)
        B = b.mindfa()
        # ops.write_graphviz(B, "test.txt")
        b = RegExpr("(True + False)* False (True + False)*", whitespace=True)
        B = b.mindfa()
        # dfa.write_graphviz("test.txt")
        c = RegExpr("(T + F)* T (T + F)*", whitespace=True,
                    alphabet=['T', 'F', 'N'])
        C = c.mindfa()
        # print "start"
        # d = RegExpr("((b?(a|c))+d)+e", syntax="regex")
        # d = RegExpr("((b?(a+c))(b?(a+c))*d)((b?(a+c))(b?(a+c))*d)*e")
        # D = d.mindfa()
        # ops.write_graphviz(D, "test.txt")
        # for s in dfa.generate(max_depth=10):
        #    print ''.join(s)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
