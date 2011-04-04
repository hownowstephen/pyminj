'''
Created on Apr 3, 2011

@author: stephen
'''

from SimpleDFA import SimpleDFA

class IntermediateTranslator:
    
    functions = []
    symboltable = None
    
    wordsize = 4
    charsize = 1
    
    count = 0
    label_count = 0
    
    DFA = None
    
    def __init__(self,symboltable):
        self.symboltable = symboltable
        # Create a new DFA object
        self.DFA = SimpleDFA()
        # Load data into the DFA
        self.DFA.Load('conf/intermediate.dfa')
        
    def TranslateSymbols(self,context):
        symbols = self.symboltable.contexts[context]
        #print symbols
    
    def TranslateFunction(self,function):
        
        frame = []
        
        print "Translating function %s" % function['name']
        
        lookup = self.symboltable.contexts['global'][function['name']]
        print lookup
        
        for line in function['listing']:
            self.DFA.Reset()
            for token in line:
                # Pull out useful details
                type = token.GetType()
                value = token.GetValue()
                # Work out our state
                self.DFA.Advance(type)
                state = self.DFA.State()
                if not state is None:
                    state = state.strip("<>")
                    self.HandleState(state)
                    
    def HandleState(self,state):
        print state
        if state == 'ASSN1': pass
            
            
                
                
                
                
                
                
                
                
                
                
                