'''
Created on 04.03.2013

@author: hlampesberger
'''
from base import Result
from vpl.vpa import VPA
import unittest



class TestVPA(unittest.TestCase):
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
        self.dvpa = VPA.build(call_alphabet=call_alphabet,
                             int_alphabet=int_alphabet,
                             ret_alphabet=ret_alphabet,
                             states=Q,
                             start_states=[q0],
                             accept_states=Qf,
                             stack_alphabet=P,
                             call_transitions=calls,
                             int_transitions=interns,
                             ret_transitions=returns)
        interns2 = [('q0', '0', 'q1'),
                   ('q0', '1', 'q0'),
                   ('q1', '0', 'q0'),
                   ('q1', '1', 'q1')]
        returns = [('q0', 'p0', '1>', 'q0'),
                   ('q0', 'p0', '1>', 'q1'),
                   ('q0', 'p1', '1>', 'q1'),
                   ('q1', 'p0', '0>', 'q0'),
                   ('q1', 'p1', '0>', 'q1')]
        calls2 = [('q0', '<1', 'q0', 'p0'),
                  ('q0', '<1', 'q0', 'p1'),
                 ('q0', '<1', 'q1', 'p0'),
                 ('q0', '<0', 'q1', 'p0'),
                 ('q1', '<1', 'q0', 'p1'),
                 ('q1', '<1', 'q0', 'p0'),
                 ('q1', '<1', 'q1', 'p1'),
                 ('q1', '<0', 'q1', 'p1')]
        self.vpa = VPA.build(call_alphabet=call_alphabet,
                             int_alphabet=int_alphabet,
                             ret_alphabet=ret_alphabet,
                             states=Q,
                             start_states=[q0],
                             accept_states=Qf,
                             stack_alphabet=P,
                             call_transitions=calls2,
                             int_transitions=interns2,
                             ret_transitions=returns)


    def test_deterministic(self):
        self.assertTrue(self.dvpa.is_deterministic())
        self.assertFalse(self.vpa.is_deterministic())


    def test_determinization(self):
        Q = [0, 1]
        acc = [1]
        start = [0]
        a_call = ['a']
        a_ret = ['b']
        a_int = ['c']
        a_stack = ['s']
        call = [(0, 'a', 0, 's'), (0, 'a', 1, 's')]
        ret = [(1, 's', 'b', 1)]
        ints = [(1, 'c', 1), (1, 'c', 0)]
        nonvpa = VPA.build(call_alphabet=a_call,
                             int_alphabet=a_int,
                             ret_alphabet=a_ret,
                             states=Q,
                             start_states=start,
                             accept_states=acc,
                             stack_alphabet=a_stack,
                             call_transitions=call,
                             int_transitions=ints,
                             ret_transitions=ret)
        nonvpa.determinize()
        # nonvpa.write_png("test.png")

    def test_membership(self):
        s1 = "1.<0.1.<1.0.0.1>.0>.0".split('.')
        # s2 = "0>.<1.1>.1>.<0.0.<1.0".split('.')
        s3 = "1.<0.1.<1.0.1.1>.0>.0".split('.')
        self.assertEqual(self.dvpa.membership(s1), Result.accept)
        self.assertEqual(self.vpa.membership(s1), Result.accept)
        self.assertEqual(self.dvpa.membership(s3), Result.reject)
        self.assertEqual(self.vpa.membership(s3), Result.accept)
        self.vpa.write_pdf()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
