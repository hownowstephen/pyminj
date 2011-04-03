'''
Created on Feb 20, 2011

@author: stephen
'''

from pyminj.Parser import Parser
from pyminj.Token import Token


p = Parser('pyminj/syntax.ll1')

p.ParseToken(Token('DATA_TYPE','class'))
p.ParseToken(Token('IDENT','awesome'))
p.ParseToken(Token('DELIMITER','{'))
p.ParseToken(Token('IDENT','rocket'))
p.ParseToken(Token('OTHER',';'))
p.ParseToken(Token('DELIMITER','}'))