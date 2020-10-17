'''
Created on 09.12.2014

@author: hlampesberger
'''
from regular.regexpr import RegExpr

if __name__ == '__main__':
    dfa1 = RegExpr("ab*").mindfa()
    dfa1.write_png("union_dfa1")
    dfa2 = RegExpr("a*b").mindfa()
    dfa2.write_png("union_dfa2")
    #dfa2 = RegexParser.parse("^a*b$").eval().to_epsilon_nfa(2).subset_construction().minimize()
    #write_png(dfa2, "dfa2.png")
    dfa = dfa1 | dfa2
    dfa.write_png("union_dfa")
    #write_png(dfa, "dfa.png")