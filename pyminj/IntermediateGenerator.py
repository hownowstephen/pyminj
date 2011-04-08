'''
Created on Apr 3, 2011

@author: stephen
'''

from ThreeCodeGenerator import ThreeCodeGenerator
from Token import Token

# Define some constants for various usage
MAIN_FUNCTION = "<main_f>"
SEMICOLON = ";"
FUNCTION_STATE = "function"
PROGRAM_STATE = "program"



class IntermediateGenerator:
    '''Generates a pre-intermediate code dataset from the parsed code'''
    
    options = None
    listing = []
    headers = []
    function = {}
    expression = []
    controlStack = []
    
    executionState = PROGRAM_STATE
    lastToken = None
    
    lineContext = []
    
    symboltable = None
    translator = None
    
    def __init__(self,symboltable):
        '''Set our symbol table'''
        self.symboltable = symboltable
                
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
        '''
        Handler for individual statements, helps break up statements and functions
        logically for the threecode generator
        '''
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
        '''
        PrintListing
        writes to file the generated listing of intermediate code
        note: Frame headers are not being written at this stage, as they will be written
              directly into the target code, to allow us another pass of the code to
              write into the headers the variable locations etc.
        '''
        for line in self.listing:
            context = line['name']
            print "\nmethod %s start" % context
            for tkset in line['listing']:
                generator = ThreeCodeGenerator(self.symboltable,tkset,context)
                generator.Parse()
            print "method %s end" % context

            