'''
Created on Apr 3, 2011

@author: stephen
'''

from IntermediateTranslator import IntermediateTranslator
from Token import Token

# Define some constants for various usage
MAIN_FUNCTION = "<main_f>"
SEMICOLON = ";"
FUNCTION_STATE = "function"
PROGRAM_STATE = "program"



class IntermediateGenerator:
    
    options = None
    listing = []
    headers = []
    function = {}
    expression = []
    controlStack = []
    
    executionState = PROGRAM_STATE
    lastToken = None
    
    symboltable = None
    translator = None
    
    def __init__(self,symboltable):
        self.symboltable = symboltable
        self.translator = IntermediateTranslator(symboltable)
                
    def HandleFunction(self,token,state):
        """
        Handler for function blocks
        """        
        if token == self.lastToken: return
        self.lastToken = None
        
        self.executionState = FUNCTION_STATE
        
        type = token.GetType()
        value = token.GetValue()
        
        if type == "BLOCK_DELIMITER":
            try:
                self.function['listing']
                self.listing.append(self.function)
                self.function = {}
            except:
                self.function['listing'] = []
                
        if type == "DATA_TYPE":
            try:
                self.function['type']
            except:
                # Function datatype
                self.function['type'] = value
                # Because main_f is interpreted differently, we have to name it manually
                if state.__str__() == MAIN_FUNCTION: self.function['name'] = "main"
                
        elif type == "IDENT" and state.__str__() != MAIN_FUNCTION:
            try:
                self.function['name']
            except:
                self.function['name'] = value
        elif type == "FLOW_CONTROL":
            self.HandleStatement(token,state)
        else:
            pass
            
    def HandleStatement(self,token,state):
        type = token.GetType()
        value = token.GetValue()
        
        if token == self.lastToken: return
        self.lastToken = token
        
        # Terminate flow control
        if value == "}":
            try:
                self.function['listing'].append([Token("FLOW_CONTROL","end%s" % self.controlStack.pop())])
            except:
                pass
        
        if value == SEMICOLON or type == "BLOCK_DELIMITER":
            self.lastToken = None
            if self.expression and self.executionState == PROGRAM_STATE:
                pass #self.listing.append(self.expression)
            elif self.expression:
                self.function['listing'].append(self.expression)
            
            self.expression = []
        elif type != "DELIMITER" or self.executionState == PROGRAM_STATE:
            self.expression.append(token)
            if type == "FLOW_CONTROL" and value != "return":
                self.controlStack.append(value)
        elif type == "DELIMITER": 
            self.expression.append(token) 
        else:
            self.lastToken = None        
    
    def PrintListing(self):
        self.symboltable.Print()
        self.translator.TranslateSymbols('global')
        for line in self.listing:
            l = line['listing']
            for s in l:
                print s
            #self.translator.TranslateFunction(line)
            