import string
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
            self.states[name] = self.count
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
        
        self.contexts = []
        #print "Handling",tokenset
        
    def AddParam(self,token):
        self.params.append(token)
    def AddAction(self,token):
        self.actions.append(token)
        
    def GetToken(self):
        return self.tokens.pop(0)
    
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
            
    def Parse(self):
        try:
            token = self.GetToken()
            # Convert the token type to a nice camelcase handler method name
            method = "Handle%s" %  string.capwords(token.GetType(),'_').replace("_","")
            try:
                function=getattr(self,method) 
                function(token)
                self.Parse()
            except:
                # import sys
                # print sys.exc_info()
                print method
                pass
        except:
            return self.ConstructCodes()       
    
    def HandleAssign(self,token):
        if self.state == tcstates.IDENT:
            self.AddAction(token)
            self.state = tcstates.ASSIGNMENT;
            
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
                self.basevar = Token("IDENT","returnvar")
                self.AddAction(token)
            self.state = tcstates.RETURN
            
    def HandleIdent(self,token):
        if self.state == tcstates.INIT:
            self.basevar = token
            self.state = tcstates.IDENT
        # Check for assignment state or return state
        elif self.state in [tcstates.ASSIGNMENT,tcstates.RETURN,tcstates.RETURN2]:
            
            if self.state == tcstates.RETURN:
                self.AddParam(token)
                self.AddAction(Token("ASSIGN","="))
                self.state = tcstates.RETURN2
                
            if not self.basevar:
                self.basevar = token
                self.AddParam(token)
            else:
                self.AddParam(token)
            
    def HandleNumeric(self,token):
        if self.state in [tcstates.RETURN,tcstates.RETURN2,tcstates.ASSIGNMENT]:
            self.AddParam(token)
    
    def HandleOperator(self,token):
        if self.state == tcstates.ASSIGNMENT:
            self.AddAction(token)
        elif self.state in [tcstates.RETURN,tcstates.RETURN2]:
            self.AddAction(token)
            self.reversed = True
    
    def HandleSystemIo(self,token):
        if self.state == tcstates.ASSIGN:
            # System.in
            pass
        elif self.state == tcstates.INIT:
            # System.out
            pass
            
            
    def ConstructCodes(self):
        codes = []
        mod = -1
        if self.reversed: mod = 0
        
        while True:
            try:
                action = self.actions.pop(mod)
                try:
                    action = self.methods[action.GetValue()]
                except:
                    action = action.GetValue()
                
                param = self.params.pop(mod).GetValue()

                if not self.basevar:
                    if not param: codes.append("%s" % (action))
                    else: codes.append("%s %s" % (action,param))
                else:
                    if not param or action in ['return',]:
                        codes.append("%s %s" % (action,self.basevar.GetValue()))
                    else:
                        codes.append("%s %s %s" % (action,self.basevar.GetValue(),param))
            except:
                break
        for line in codes:
            print line
            
            
            
            
            
            