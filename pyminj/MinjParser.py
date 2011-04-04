'''
Created on Apr 3, 2011

@author: stephen
'''
from Parser import Parser
import re
from Errors import SyntaxException

class MinjParser(Parser):
    
    Version = "1.2.1"
    Author = "st_youn"
    
    execState = None
    new = True    
    generator = None
    
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
            return self.ParseToken(token)
        
        # Load the next element we're looking for
        elem = currState.NextElement()
        
        self.handleState(token,currState)
        
        if re.match('<\w+>',elem.__str__()):
            newState = self.AddState(elem,tkvalue)
            
            if (tkvalue in newState.GetLookahead()):
                return self.ParseToken(token)
            elif newState.IsNullable():
                self.state.pop()
                return self.ParseToken(token)
            
        if elem and tkvalue in elem: 
            return currState
            # print tkvalue
        # Otherwise, test if we can nullify the current state instead and retry
        elif currState.IsNullable():
            self.state.pop()
            return self.ParseToken(token)
        
        else:
            raise SyntaxException("Token %s cannot go here" % tkvalue)
            
    def handleState(self,token,currState):
        stripped = currState.__str__().strip("< >")
        self.execState = stripped
        try:
            function=getattr(self,"fn_%s" % stripped) 
            function(token,currState)    
        except:
            if token.GetType() == "BLOCK_DELIMITER":
                self.generator.HandleStatement(token,currState)
        
    ''' Functions '''
    def fn_funct_def(self,token,state):
        if self.new: self.generator.HandleFunction(token,state)
        
    def fn_main_f(self,tk,st): return self.fn_funct_def(tk,st)
            
    ''' Statements '''
    def fn_exp(self,token,state):
        if self.new: 
            self.generator.HandleStatement(token,state)
    def fn_st(self,tk,st): return self.fn_exp(tk,st)
    def fn_prim(self,tk,st): return self.fn_exp(tk,st)
    def fn_mult_op(self,tk,st): return self.fn_exp(tk,st)
    def fn_decl(self,tk,st): return self.fn_exp(tk,st)
    def fn_NEW(self,tk,st): return self.fn_exp(tk,st)
    def fn_N1(self,tk,st): return self.fn_exp(tk,st)
    def fn_M1(self,tk,st): return self.fn_exp(tk,st)
    def fn_add_op(self,tk,st): return self.fn_exp(tk,st)
    def fn_v_list(self,tk,st): return self.fn_exp(tk,st)