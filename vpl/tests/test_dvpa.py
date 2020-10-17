'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from vpl.dvpa import DVPA
import unittest






class TestDVPA(unittest.TestCase):
    def setUp(self):
        int_alphabet = ['0', '1']
        call_alphabet = ['<0', '<1']
        ret_alphabet = ['0>', '1>']
        Q = ['q0', 'q1']
        P = ['p0', 'p1']
        q0 = 'q0'
        Qf = Q
        calls = [('q0', '<1', 'q0', 'p0'),
                 ('q0', '<0', 'q1', 'p0'),
                 ('q1', '<1', 'q0', 'p1'),
                 ('q1', '<0', 'q1', 'p1')]
        interns = [('q0', '0', 'q1'),
                   ('q0', '1', 'q0'),
                   ('q1', '0', 'q0'),
                   ('q1', '1', 'q1')]
        returns = [('q0', 'p0', '1>', 'q0'),
                   ('q0', 'p1', '1>', 'q1'),
                   ('q1', 'p0', '0>', 'q0'),
                   ('q1', 'p1', '0>', 'q1')]
        self.dvpa = DVPA.build(call_alphabet=call_alphabet,
                             int_alphabet=int_alphabet,
                             ret_alphabet=ret_alphabet,
                             states=Q,
                             start_state=q0,
                             accept_states=Qf,
                             stack_alphabet=P,
                             call_transitions=calls,
                             int_transitions=interns,
                             ret_transitions=returns)



    def test_membership(self):
        s1 = "1.<0.1.<1.0.0.1>.0>.0.1.1.1".split('.')
        s3 = "1.<0.1.<1.0.1.1>.0>.0".split('.')
        self.assertEqual(self.dvpa.membership(s1), Result.accept)
        self.assertEqual(self.dvpa.membership(s3), Result.reject)
        # print self.dvpa.parse(s2, ['p', 'p'])

    def test_complete(self):
        self.assertFalse(self.dvpa.is_complete())
        self.dvpa.complete()
        self.assertTrue(self.dvpa.is_complete())
#        for i in self.dvpa.itercalls():
#            print i
#        for i in self.dvpa.iterinterns():
#            print i
#        for i in self.dvpa.iterreturns():
#            print i
        # self.dvpa.write_png("test.png", exclude_states={-1})

    def test_rename(self):
        vpa2 = self.dvpa.rename()
        self.assertEqual(vpa2.states, {0, 1})



    def test_union_intersection(self):
        # self.dvpa.write_png("test0.png")
        un = (self.dvpa | self.dvpa)
        inter = (self.dvpa & self.dvpa)
        s1 = "1.<0.1.<1.0.0.1>.0>.0.1.1.1".split('.')
        s3 = "1.<0.1.<1.0.1.1>.0>.0".split('.')
        self.assertEqual(un.membership(s1), Result.accept)
        self.assertEqual(un.membership(s3), Result.reject)
        self.assertEqual(inter.membership(s1), Result.accept)
        self.assertEqual(inter.membership(s3), Result.reject)
        # un.write_png()
        # inter.write_pdf()
        # TODO: union, intersection of VPA testing
1

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
