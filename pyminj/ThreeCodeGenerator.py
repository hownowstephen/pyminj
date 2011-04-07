import string,sys
from Token import Token

class RuntimeEnum:
    ''' 
    Generates enumerated values on the fly, used initially
    for developing a recursive state machine
    '''
    def __init__(self): 
        self.count = 0
        self.states = {}
    def __getattr__(self,name):
        try:
            self.states[name]
        except:
            self.states[name] = name
            self.count += 1
        return self.states[name]
    
tcstates = RuntimeEnum()
tcmodes = RuntimeEnum()

class ThreeCodeGenerator:
    
    methods = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod", 
               "&&": "and", "||": "or", "=": "assign","<": "lt", ">": "gt", 
               "<=": "lte", ">=": "gte", "!=": "ne"}
    
    def __init__(self,symboltable,tokenset,context):
        
        self.symbols = symboltable
        self.tokens = tokenset
        self.output = []
        self.state = tcstates.INIT;
        self.reversed = False
        
        self.basevar = None
        self.actions = []
        self.params = []
        
        self.codes = []
        self.tmp = -1
        self.currOperator = None
        
    def AddParam(self,token):
        self.params.append(token)
    def AddAction(self,token):
        self.actions.append(token)
        
    def AddCode(self,param,operator=None,base=None):
        
        if operator == 'return': 
            self.codes.append(operator)
            return
        
        # Check for an operator override
        if operator: op = operator
        else: op = self.currOperator
        try: op = self.GetMethod(op)
        except: pass
        # Check if there is a base var override
        if base: b = base
        else: b = self.basevar
        try: b = b.GetValue()
        except: pass
        
        try: param = param.GetValue()
        except: pass
        self.codes.append("%s %s %s" % (op,b,param))
    
    def IncTmp(self):
        self.tmp = self.tmp + 1;
        if self.tmp > 12:
            self.tmp = 0 
        return "tmp%i" % self.tmp   
    
    def GetToken(self):
        return self.tokens.pop(0)
    
    def GetMethod(self,token):
        if token.GetValue() in self.methods:
            return self.methods[token.GetValue()]
        else:
            return token.GetValue()
    
    def Find(self,ident):
        if ident is None: return None
        try:
            return ident.GetValue()
        except:
            try:
                if ident['type'] == 'function':
                    return ident['name']
                raise Exception
            except:
                return ident['name']
            
    def Parse(self,construct=True):
        try:
            token = self.GetToken()
            # Convert the token type to a nice camelcase handler method name
            method = "Handle%s" %  string.capwords(token.GetType(),'_').replace("_","")
            try:
                function=getattr(self,method) 
                function(token)
                self.Parse()
            except:
                print method
                pass
        except:
            if construct:
                return self.ConstructCodes()       
    
    def HandleAssign(self,token):
        self.currOperator = token
        self.state = tcstates.ASSIGNMENT
            
    def HandleDelimiter(self,token):
        if self.state == tcstates.INIT:
            pass
            
    def HandleFlowControl(self,token):
        value = token.GetValue()
        if self.state == tcstates.INIT:
            if value != "return":
                # Handle other flow control
                pass
            else:
                self.state = tcstates.RETURN
                self.basevar = Token("IDENT","return")
                self.currOperator = Token("OPERATOR","=")
            #self.state = tcstates.RETURN
            
    def HandleIdent(self,token):
        if self.state == tcstates.INIT:
            self.basevar = token
            self.state = tcstates.IDENT
        # Check for assignment state or return state
        elif self.state in [tcstates.ASSIGNMENT,tcstates.RETURN,tcstates.RETURN2]:
            
            if self.state == tcstates.RETURN:
                self.AddCode(token)
                self.state = tcstates.RETURN2
                
            if not self.basevar:
                self.basevar = token
                self.AddParam(token)
            else:
                self.AddParam(token)
            try:
                next = self.GetToken()
                if next.GetType() == "OPERATOR":
                    self.HandleOperator(next)
                # Handle embedded function calls
                elif next.GetType() == "DELIMITER" and next.GetValue() == "(":
                    target = self.CallFunction(token.GetValue())
                    if not self.currOperator is None:
                        self.AddCode(target)
                        self.currOperator = None
                else:
                    # Push back to be handled by the parser
                    self.tokens.push(next)
            except:
                pass
        
    def CallFunction(self,fn):
        param = 1
        while True:
            try:
                token = self.GetToken()
                #print token
                if token.GetType() == "DELIMITER":
                    # end of the loop
                    if token.GetValue() == ")": break
                    # Ignore commas
                    elif token.GetValue() == ",": continue
                self.codes.append("assign %s_p%i %s" % (fn,param,token.GetValue()))
                param = param + 1
            except:
                break
        target = self.IncTmp()
        self.codes.append("assign %s_return %s" % (fn,target))
        self.codes.append("call %s" % fn)
        return target
        
        
            
    def HandleNumeric(self,token):
        if self.state in [tcstates.RETURN,tcstates.RETURN2,tcstates.ASSIGNMENT]:
            self.codes.append("%s %s %s" % (self.GetMethod(self.currOperator),self.basevar.GetValue(),token.GetValue()))
            self.currOperator = None
    
    def HandleOperator(self,token):
        self.currOperator = token
        
    def HandleOpMinus(self,token):
        self.currOperator = token
    
    def HandleSystemIo(self,token):
        if self.state == tcstates.ASSIGN:
            # System.in
            pass
        elif self.state == tcstates.INIT:
            # System.out
            pass
            
            
    def ConstructCodes(self):
        if self.state == tcstates.RETURN2:
            self.AddCode(None,"return",None)
        for code in self.codes:
            print code
            
            
            
            
            
            