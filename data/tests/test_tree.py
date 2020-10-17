'''
Created on 04.03.2013

@author: hlampesberger
'''
import unittest
from data.tree import Tree, Node



class TestTree(unittest.TestCase):
    def test_basics(self):
        d = Tree("d")
        self.assertEqual(len(d), 1)
        self.assertEqual(list(iter(d)), [Node("d")])
        c = Tree("c")
        b = Tree("b", [d])
        t = Tree("a", [b, c])
        self.assertTrue(t.is_root(t.root))
        self.assertEqual(t.leaves(), {d.root, c.root})
        self.assertEqual(len(t), 4)
        self.assertEqual(t.depth(), 3)
        self.assertEqual(t.nodelevel(t.root), 1)
        self.assertEqual(t.nodelevel(b.root), 2)
        self.assertEqual(t.nodelevel(c.root), 2)
        self.assertEqual(t.nodelevel(d.root), 3)
        self.assertEqual(t.k_root(t.depth()), t)

    def test_parse_equality(self):
        self.assertEqual(Tree.parse("a()"), Tree.parse("a()"))
        self.assertNotEqual(Tree.parse("a()"), Tree.parse("b()"))
        self.assertEqual(Tree.parse("a(b()c())"), Tree.parse("a(b()c())"))
        self.assertNotEqual(Tree.parse("a(b()c())"), Tree.parse("a(c()b())"))

    def test_tree_properties(self):
        # from Kosala et al. (2003): "Information extraction from Web documents
        # based on local unranked tree automaton inference"
        t = Tree.parse("a(b(a(b()x()))c())")
        # t.write_graphviz("test.txt")
        self.assertEqual(len(t), 6)
        self.assertEqual(t.depth(), 4)
        self.assertEqual(t.nodelevel(t.root), 1)
        self.assertEqual(t, t.copy())
        self.assertEqual(list(t.level(2)), [Node("b"), Node("c")])
        self.assertEqual(list(t.level(3)), [Node("a")])
        self.assertTrue(t.nodelevel(list(t.level(3))[0]), 3)
        for i in xrange(1, t.depth() + 1):
            self.assertTrue(all([t.nodelevel(n) == i for n in t.level(i)]))
        t2 = Tree.parse(str(t))
        self.assertEqual(t, t2)


    def test_xml(self):
        t = Tree.parse("a(b()b(b()c(a()a())))")
        t2 = Tree.parse(str(t))
        self.assertEqual(t2.to_xml(),
                         "<a><b></b><b><b></b><c><a></a><a></a></c></b></a>")


    def test_tree_manipulation(self):
        t = Tree.parse("a(a(a(a()b()))b())")
        fork1 = Tree.parse("a(a(a())b())")
        fork2 = Tree.parse("a(a(a()b()))")
        st1 = Tree.parse("a()")
        st2 = Tree.parse("b()")
        st3 = Tree.parse("a(a()b())")
        root2 = Tree.parse("a(a()b())")
        elems = [st1, st2, st2, st3]
        # t.write_graphviz("test.txt")
        self.assertEqual(t.k_root(2), root2)
        for st in t.k_subtree(2):
            ind = elems.index(st)
            elems.pop(ind)
        self.assertFalse(elems)
        elems = [fork1, fork2]
        for st in t.k_fork(3):
            ind = elems.index(st)
            elems.pop(ind)
        self.assertFalse(elems)



    def test_nested_word(self):
        t = Tree.parse("a(b()b(b()c(a()a())))")
        self.assertEqual(t.k_root(4), t)
        l = t.to_word()
        a = t.tagged_alphabet()
        self.assertEqual(a, {("<a", "a>"), ("<b", "b>"), ("<c", "c>")})
        self.assertEqual(l, ['<a', '<b', 'b>', '<b', '<b', 'b>', '<c', '<a',
                             'a>', '<a', 'a>', 'c>', 'b>', 'a>'])

    def test_subtree(self):
        t = Tree.parse("a(b())")
        for i in t.k_subtree(1):
            self.assertEqual(i, Tree.parse("b()"))

    """
    def test_serialization(self):
        import automata.contextfree.cfg
        cfg = automata.contextfree.cfg.ContextFreeGrammar("S")
        cfg.add_rule("S -> node")
        cfg.add_rule("node -> name '(' node node ')' | name '(' ')' ")
        cfg.add_rule("name -> 'a' | 'b' | 'c'")   
        #cfg.to_2NF()
        #cfg.print_rules()
        #print cfg.is_2NF, cfg.is_CNF
        strng = ''.join(cfg.derive_random())
        print strng
        t = Tree.parse(strng)
        #t.write_graphviz("test.txt")
        print t
        print t.to_xml()
        print 
        print "root", t.k_root(2)
        for i in t.k_fork(3):
            print "fork", i
        for i in t.k_subtree(2):
            print "subt", i
        

    def _test_example_dtd(self):
        import automata.contextfree.cfg
        cfg = automata.contextfree.cfg.ContextFreeGrammar("dealer")
        cfg.add_rule("dealer -> 'dealer(newcar(' new_cars ')usedcar(' used_cars '))'")
        cfg.add_rule("new_cars -> new_ad new_cars | new_ad")
        cfg.add_rule("used_cars -> used_ad used_cars | used_ad")
        cfg.add_rule("new_ad -> 'ad(' model '(PCDATA()))'")
        cfg.add_rule("used_ad -> 'ad(' model '(PCDATA())' year '(PCDATA()))'")
        cfg.add_rule("model -> 'model'")
        cfg.add_rule("year -> 'year'")
        #cfg.to_2NF()
        #cfg.print_rules()
        #print cfg.is_2NF, cfg.is_CNF
        strng = ''.join(cfg.derive_random())
        print strng
        t = Tree.parse(strng)
        #t.write_graphviz("test.txt")
        print t
        print t.to_xml()
        print
        print "root", t.k_root(2)
        for i in t.k_fork(3):
            print "fork", i
        for i in t.k_subtree(2):
            print "subt", i
        """


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
