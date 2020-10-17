'''
Created on 29.08.2013

@author: hlampesberger
'''
from regular.regexpr import RegExpr


if __name__ == '__main__':
    r = RegExpr("(a+b)*ab(a+b)*")
    print r
    r.mindfa().write_png()
