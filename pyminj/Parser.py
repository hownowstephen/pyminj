#!/usr/bin/env python

'''
@package PyMinJ
@class Parser
@brief Reads a token stream and compares it to an input grammar to ensure its syntax
@note All documentation can be found in /doc/
@author Stephen Young (st_youn@encs.concordia.ca)
'''

from Syntax import Syntax
from SymbolTable import SymbolTable
import re
from Errors import SyntaxException,MissingTokenException

class Parser(object):
    """@class Parser"""
    
    Version = "1.1.0"
    Author = "st_youn"
    
    syntax = None
    state = []
    
    parsedToken = False
    
    
    def __init__(self,cfg,INIT='prg'):
        
        # Load the syntax parser and the first known state
        self.syntax = Syntax(cfg)
        self.startState = INIT
        self.started = False
        self.symboltable = SymbolTable("conf/symboltable.cb")
            
    def ParseToken(self,token):
        ''' Main function, performs the actual parsing '''
        # Get the value of the current token passed to the parser
        tkvalue = token.SyntaxValue()
        
        if not self.started: 
            self.AddState(self.startState,tkvalue)
            self.started = True
            
        # If we don't have any accessible states, exit
        if not self.state: 
            self.parsedToken = False
            return
        # Load the next state based on the token's identity
        currState = self.state[len(self.state)-1]
        
        # If the state stack is empty, remove it and re-run the token parsing command
        if not currState: 
            self.state.pop()
            return self.ParseToken(token)
        
        # Load the next element we're looking for
        elem = currState.NextElement()
        
        if not self.parsedToken:
            self.symboltable.HandleState(currState.__str__(),token)
            self.parsedToken = True
        
        # If we have a variable, enter the variable's state, and re run this function
        if re.match('<\w+>',elem.__str__()):
            newState = self.AddState(elem,tkvalue)
            # print "State: ",elem.__str__()
            #print "Lookahead: ", newState.GetLookahead(),newState.IsNullable()
            # Checks that our current syntactic token has a proper lookahead for the current state
            if (tkvalue in newState.GetLookahead()):
                #print "Our token is in the lookahead!"
                return self.ParseToken(token)
            # If the lookahead fails, fallback on the nullability of the state
            elif newState.IsNullable():
                self.state.pop()
                return self.ParseToken(token)
            # Otherwise this is an invalid token for this context, so we die
            else:
                print "Lookahead: ", newState.GetLookahead(),newState.IsNullable()
                print "Varerror: looking for ", elem
                raise SyntaxException("Token %s cannot go here" % tkvalue)
                return
        
        #print "Testing if ",tkvalue," is in ",elem
        # If the element matches the current token value, continue
        if tkvalue in elem: 
            return currState
            # print tkvalue
        # Otherwise, test if we can nullify the current state instead and retry
        elif currState.IsNullable():
            print currState
            self.state.pop()
            return self.ParseToken(token)
        else:   
            print currState
            options = "%s" % ','.join(elem)  
            raise SyntaxException("Looking for %s, found %s" % (options,tkvalue))
            return
            
    def AddState(self,stateID,la=None):
        ''' Adds a state to the stack '''
        state = self.syntax.GetState(stateID,la)
        if state: self.state.append(state)
        return self.state[len(self.state)-1]
    
    def CheckStack(self):
        ''' Checks if the stack is empty, otherwise throws an error '''
        empty = True
        if self.state:
            for s in self.state:
                empty = empty and s.StackEmpty()
        if not empty:
            raise MissingTokenException("Code block not terminated, missing %s" % self.GetNextStackItem())
        return empty
    
    def GetNextStackItem(self):
        ''' Used for error reporting, gets the next token we were looking for'''
        for s in reversed(self.state):
            if not s.StackEmpty():
                for i in reversed(s.Stack):
                    if not re.match('<[a-zA-Z0-9_]+>',i):
                        return i
        # Shouldn't reach this ever, but better safe than sorry
        return 'UNKNOWN'
    
    def SetIntermediateCodeGenerator(self,generator):
        self.generator = generator;
    
    def GetVersion(self):
        return "%s (%s)" % (self.Version, self.Author)