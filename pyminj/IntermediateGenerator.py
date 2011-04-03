'''
Created on Apr 3, 2011

@author: stephen
'''

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
    
    executionState = PROGRAM_STATE
    lastToken = None
    
    def __init__(self,symboltable):
        print "Initialized generator"
        self.symboltable = symboltable
        
    def HandleBranch(self,token,state):
        print "Handling a branching action"
                
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
                print "Closing Function: %s" % value
                print self.function
                self.listing.append(self.function)
                self.function = {}
            except:
                self.function['listing'] = []
                print "Opening Function: %s" % value
        elif type == "DATA_TYPE":
            try:
                self.function['type']
            except:
                # Function datatype
                self.function['type'] = value
                # Because main_f is interpreted differently, we have to name it manually
                if state.__str__() == MAIN_FUNCTION: self.function['name'] = "main"
                
        elif type == "IDENT" and state.__str__() != MAIN_FUNCTION:
            self.function['name'] = value
        elif type == "FLOW_CONTROL":
            self.HandleStatement(token,state)
        else:
            print "%s: %s" % (type,value)
            
    def HandleStatement(self,token,state):
        type = token.GetType()
        value = token.GetValue()
        print "Last token: ",self.lastToken       
        if token == self.lastToken: return
        self.lastToken = token
        print "Handling a statement: %s,%s" % (value,type)
        
        if value == SEMICOLON or type == "BLOCK_DELIMITER":
            self.lastToken = None
            if self.expression and self.executionState == PROGRAM_STATE:
                self.listing.append(self.expression)
            elif self.expression:
                self.function['listing'].append(self.expression)
            self.expression = []
        elif type != "DELIMITER" or self.executionState == PROGRAM_STATE:
            self.expression.append(token)
            print self.expression
        else:
            self.lastToken = None
            print "IGNORED %s" % value
            
    
    def PrintListing(self):
        
        for line in self.headers:
            print "Printing header"
        
        for line in self.listing:
            print line
            