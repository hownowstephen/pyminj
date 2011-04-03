#!/usr/bin/env python

'''
@package PyMinJ
@class Syntax
@brief Loads a syntax document, parses and creates a traversable syntax class
@note All documentation can be found in /doc/
@author Stephen Young (st_youn@encs.concordia.ca)
'''

import re, fileinput, sys
from copy import deepcopy
from time import sleep

class SyntaxState:
    '''
    @class SyntaxState
    @brief Represents a single reachable state in the parser
           and is associated with a certain type of token. 
    @note Tokens __str__ value is what will be compared to ensure that they are of an equivalent type
    '''
    Nullable = False
    Lookahead = []
    Stack = []
    ID = ''
    
    def __init__(self,ident,stack,la):
        '''Generates a syntactic stack,and generates lookaheads'''
        # Load the stack as a queue and reverse it
        self.ID = ident
        self.Stack = stack
        self.Stack.reverse()
        # Parse the lookahead string
        self.Lookahead = self.ParseLookahead(la)
        
    def NextElement(self):
        '''Gets the next element required to continue in this state'''
        if len(self.Stack) > 0:
            # Pop the element and then check if the element needs to be split
            elem = self.Stack.pop()
            if elem.find("`") > 0: elem = elem.split("`")
            return elem
        return False
    
    def ParseLookahead(self,la):
        '''Parses the lookahead string from the config'''
        # Deal with nullable values
        if la.find("|") > 0:
            la = la.split("|")
            if la[0] == 'e': self.Nullable = True 
            la = la[1]
        return la.split("`")
    
    def GetLookahead(self):
        '''Gets the lookahead'''
        return self.Lookahead
    
    def IsNullable(self):
        '''Gets whether this state is nullable'''
        return self.Nullable
    
    def StackEmpty(self):
        '''Gets whether this state has been completed'''
        if not self.Stack:
            return True
        return False
    
    def __str__(self):
        '''Debug info for printing out this state'''
        return "<%s>" % self.ID
    # return 'State %s Stack: [' % self.ID + ','.join(self.Stack) + ']'
    
    def __nonzero__(self):
        '''Override to allow us to check the truth value of this class'''
        if not self.Stack: return False
        return True
    

class Syntax:
    '''
    @class Syntax
    @brief Loads the available states from a configuration file and works directly
           with the main parsing program to manage the current state of the application
    '''
    States = {}
    
    def __init__(self,file):
        '''Reads the configuration file and parses it into a set of stored states'''
        # Basic syntax configuration file parser
        for line in fileinput.input([file]):
            # Remove comments
            line = line.strip()
            index = line.find('#')
            if index >= 0: line = line[:index].strip()
            # Ignore empty lines
            if len(line) > 0:
                s = line.split('->')
                if not s is None:
                    state,LA = self.ParseState(s[0].strip()) 
                    tokens = s[1].strip().split(' ')
                    # If the state has not been previously defined, create an empty list
                    if not state in self.States: self.States[state] = []
                    # Append the state
                    self.States[state].append(SyntaxState(state,tokens,LA))
        # Done parsing states
        #for key,value in self.States.iteritems():
        #    print value.GetLookahead()
                
    def ParseState(self,raw):
        '''Parses an individual state'''
        state_regex = r"\<(?P<state>[a-zA-Z0-9_]+)\>\W+\((?P<LA>.+)\)"
        m = re.match(state_regex,raw)
        return m.group('state'),m.group('LA')
    
    def GetState(self,state,la):
        '''Returns a deep copy of the requested state'''
        state = state.strip('<> ')
        if state in self.States:
            for s in self.States[state]:
                if la in s.GetLookahead() or s.IsNullable():
                    # Always return a deep copy to ensure that state details are not overridden
                    return deepcopy(s)
        return False
        
                