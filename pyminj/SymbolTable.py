'''
@package PyMinJ
@class Scanner
@brief Manages the parsing and creation of a multidimensional symbol table for the given input
@note All documentation can be found in /doc/
@author Stephen Young (st_youn@encs.concordia.ca)
'''

import fileinput
from Errors import IdentifierExistsException

class SymbolTable:
    
    callbacks = {}
    currState = None
    currIdentifier = {}
    
    # Management of programmatic context
    bracketLevel = 0
    contextbl = 0
    context = "global"
    contexts = {}
    
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
                    self.callbacks[s[0].strip()] = s[1].strip()
        self.contexts[self.context] = {}
                    
    def HandleState(self,state,token):
        '''Main function for handling the current state + token combination'''
        # Always refresh the state when we hit an EOL
        if token.GetValue() == ";": self.RefreshState()
        
        # Monitor brackets to determine when contexts stop and start
        if token.GetValue() == "{": self.bracketLevel += 1;
        if token.GetValue() == "}": self.bracketLevel -= 1;
        
        # Close the context if need be
        if self.bracketLevel < self.contextbl:
            self.CloseContext()
        
        # Attempt to call a callback as defined in the configuration file
        try: 
            # Load the local function referenced by the callback mechanism
            function = getattr(self,self.callbacks[state.__str__()])
            # Exec the function with the token as a param
            function(token)
        # Fail gracefully, no callback = not important to symbol table
        except:
            pass
    
    def HandleProgram(self,token):
        '''Placeholder for any initialization logic that may be needed later on'''
        pass
    
    def HandleCurrent(self,token):
        ''' Discerns the current state and loads the handler, or fails quietly'''
        try:
            return {"IDENTIFIER": self.HandleIdentifier,
                      "ARRAY": self.HandleArray,
                      "FUNCTION": self.HandleFunction}[self.currState](token)
        except:
            self.RefreshState()
    
        
    def HandleIdentifier(self,token):
        '''Handles parsing the individual details of an identifier'''
        type = token.GetType()
        value = token.GetValue()
        
        self.currState = "IDENTIFIER"
        # Handle data type declaration
        if type == "DATA_TYPE":
            self.currIdentifier['type'] = "identifier"
            try:
                self.currIdentifier['datatype']
                self.currParamType = value
            except:
                self.currIdentifier['datatype'] = value
        elif type == "IDENT":
            self.currIdentifier['name'] = value
        elif type == "DELIMITER":
            # Pass logic to an array handler next token
            self.currState = "ARRAY"
        else:
            pass
    
    def HandleArray(self,token):
        '''Handles parsing of array elements'''
        self.currIdentifier['type'] = "array"
        # Handles new array identifiers
        if token.GetType() == "NUMERIC":
            self.currIdentifier['size'] = token.GetValue()
        elif token.GetType() == "IDENT":
            self.currIdentifier['name'] = token.GetValue()
    
    def HandleFunction(self,token):
        '''Handles parsing of function signature'''        
        type = token.GetType()
        
        value = token.GetValue()
        self.currState = "FUNCTION"
        self.currIdentifier['type'] = "function"
        # Handle data type declaration
        if type == "DATA_TYPE":
            # If the datatype is already set, we must be dealing with a param
            try:
                self.currIdentifier['datatype']
                self.currParamType = value
            # otherwise set the datatype
            except:
                self.currIdentifier['datatype'] = value
        elif type == "IDENT":
            # If the name is not set we are workign with the function
            if self.currIdentifier['name'] is None:
                self.currIdentifier['name'] = value
            # Otherwise we are workign with a parameters
            else:
                try:
                    self.currIdentifier['params']
                    self.currParamType = None
                except:
                    self.currIdentifier['params'] = []
                
                self.currIdentifier['params'].append({"datatype":self.currParamType,"name":value});                    
        # New block delimiter token allows us to ensure the function signature is complete
        elif type == "BLOCK_DELIMITER":
            self.OpenContext(self.currIdentifier['name'])
            self.RefreshState()
        else:
            pass
            
    def HandleMain(self,token):
        '''Handles the main function, passes handler to HandleFunction'''
        self.currIdentifier['name'] = 'main'
        return self.HandleFunction(token)
    
    def RefreshState(self):
        '''Refreshes the current state of the parsing mechanism, and inserts the new data'''
        if self.currIdentifier:
            ident = self.currIdentifier
            self.currIdentifier = {'name':None}
            self.Insert(ident)
        self.currState = None
        return True
    
    def OpenContext(self,contextID):
        '''Opens a new logical context (function)'''
        self.context = contextID
        self.contextbl = self.bracketLevel
        
    def CloseContext(self):
        '''Closes the current logical context and returns to global'''
        self.context = "global"
        self.contextbl = 0
    
    def Insert(self,ItemData):
        '''Inserts an item into the symbol table - will throw errors if an invalid collision occurs'''
        name = ItemData['name']
        if not self.context in self.contexts.keys() and self.context:
            self.contexts[self.context] = {}
        if not name is None:
            target = self.context
            if ItemData['type'] == "function": target = "global"
            if not name in self.contexts[target].keys():
                self.contexts[target][ItemData['name']] = ItemData
            elif not name is 'main':
                raise IdentifierExistsException("Could not redeclare %s" % name)
            
    def Search(self,Scope,Identifier):
        '''Tests the current scope as well as the global scope for a given identifier, false on error'''
        try:
            return self.contexts[Scope][Identifier]
        except:
            try:
                return self.contexts['global'][Identifier]
            except:
                return False
    
    def Print(self):
        '''Debug function, prints the entire symbol table'''
        for context,data in self.contexts.iteritems():
            print "CONTEXT: %s" % context
            for c in data.itervalues():
                print c
    