'''
Created on Apr 3, 2011

@author: stephen
'''
from Parser import Parser
import re
from Errors import SyntaxException

class MinjParser(Parser):
    
    execState = None
    new = True    
    
    def ParseToken(self,token,newToken=True):
        
        self.new = newToken
        
        ''' Refactored Parser'''
        tkvalue = token.SyntaxValue()
        
        if not self.started: 
            self.AddState(self.startState,tkvalue)
            self.started = True
            
        # If we don't have any accessible states, exit
        if not self.state: 
            self.parsedToken = False
            print "No more available states"
            return
        
        # Load the next state
        currState = self.state[len(self.state)-1]
        
        # If the state stack is empty, remove it and re-run the token parsing command
        if not currState: 
            self.state.pop()
            return self.ParseToken(token,False)
        
        # Load the next element we're looking for
        elem = currState.NextElement()
        
        self.handleState(token,currState)
        
        if re.match('<\w+>',elem.__str__()):
            newState = self.AddState(elem,tkvalue)
            
            if (tkvalue in newState.GetLookahead()):
                return self.ParseToken(token,False)
            elif newState.IsNullable():
                self.state.pop()
                return self.ParseToken(token,False)
            
        if elem and tkvalue in elem: 
            print tkvalue
            return currState
            # print tkvalue
        # Otherwise, test if we can nullify the current state instead and retry
        elif currState.IsNullable():
            print currState
            self.state.pop()
            return self.ParseToken(token,False)
        
        else:
            print "Lookahead: ", newState.GetLookahead(),newState.IsNullable()
            print "Varerror: looking for ", elem
            raise SyntaxException("Token %s cannot go here" % tkvalue)
            
    def handleState(self,token,currState):
        stripped = currState.__str__().strip("< >")
        self.execState = stripped
        print "Handling %s" % stripped
        try:
            function=getattr(self,"fn_%s" % stripped) 
            function(token,currState)    
        except:
            pass
        
    def fn_prg(self,token,currState):
        if self.new:
            print token, currState.GetLookahead()
    
    def fn_decl(self,token,currState):
        if self.new:
            print token, currState.GetLookahead()
        
    def fn_main_f(self,token,currState):
        if self.new:
            print token, currState.GetLookahead()
    
    def fn_funct_def(self,token,currState):
        if self.new:
            print token, currState.GetLookahead()
    
    def fn_par_list(self,token,currState):
        if self.new:
            print token, currState.GetLookahead()
    
    def fn_p_type(self,token,currState):
        if self.new:
            print token, currState.GetLookahead() 