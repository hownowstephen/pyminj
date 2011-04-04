'''
Created on Apr 3, 2011

@author: stephen
'''

from SimpleDFA import SimpleDFA
from ThreeCodeCommand import ThreeCodeCommand

class IntermediateTranslator:
    
    frames = []
    symboltable = None
    
    wordsize = 4
    charsize = 1
    
    count = 0
    label_count = 0
    
    DFA = None
    
    currCode = None
    nextMethod = []
    
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
        self.currOffset = 0
        
        function_name = function['name']
        
        print "Translating function %s" % function_name
        
        lookup = self.symboltable.contexts['global'][function_name]
        
        for line in function['listing']:
            print line
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
                    code = self.HandleState(state,token,function_name)
                    if code: frame.append(code)
                    
            if self.currCode: frame.append(self.currCode)
            self.currCode = None
            
            for m in self.nextMethod:
                tmp = ThreeCodeCommand(self.currOffset)
                tmp.SetMethod(m['method'])
                tmp.SetParam(m['param1'])
                tmp.SetParam(m['param2'])
                frame.append(tmp)
                
            self.nextMethod = []
        for code in frame:
            print code.Encode(self.symboltable)
    
    def Lookup(self,ident,context):
        try:
            try:
                # Check locally defined variables
                return self.symboltable.contexts[context][ident]
            except:
                # Check parameters
                for param in self.symboltable.contexts['global'][context]['params']:
                    if param['name'] == ident:
                        return param
                    # Transfer to exception handler
                    raise Exception
        except:
            # Check globals
            return self.symboltable.contexts['global'][ident]
    
    def HandleState(self,state,token,fname):
        
        type = token.GetType()
        
        if self.currCode is None:
            self.currCode = ThreeCodeCommand(self.currOffset)
            self.currOffset += 1
        
        code = None
        # All assignment states"
        if state.strip("123") == "ASSN":
            if type == "IDENT":
                param = self.Lookup(token.GetValue(),fname)
                code = self.currCode.SetParam(param)
            elif type == "NUMERIC":
                code = self.currCode.SetParam(token)
            else:
                self.currCode.SetMethod(token.GetValue())
            if state == "ASSN3":
                #code = self.currCode.SetParam(token)
                self.currCode.SetMethod("setparam")
        # All branch states
        if state.strip("123") == "BRANCH":
            if type == "IDENT":
                param = self.Lookup(token.GetValue(),fname)
                code = self.currCode.SetParam(param)
            elif type == "NUMERIC":
                code = self.currCode.SetParam(token)
            else:
                method = self.currCode.SetMethod(token.GetValue())
                if method: 
                    self.nextMethod.append(method)   
        if code: 
            self.currCode.ResetParam2()
            print "CODE:",code
            return code
            
            
                
                
                
                
                
                
                
                
                
                
                