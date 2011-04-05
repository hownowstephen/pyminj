
import string

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
        
        #print "Handling",tokenset
        
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
            self.actions.append(token)
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
                self.actions.append(value)
            self.state = tcstates.RETURN
            
    def HandleIdent(self,token):
        if self.state == tcstates.INIT:
            self.basevar = token
            self.state = tcstates.IDENT
        elif self.state == tcstates.ASSIGNMENT or self.state == tcstates.RETURN:
            if not self.basevar:
                self.basevar = token
                self.params.append(token)
            else:
                self.params.append(token)
            
    def HandleNumeric(self,token):
        if self.state == tcstates.RETURN or self.state == tcstates.ASSIGNMENT:
            self.params.append(token)
    
    def HandleOperator(self,token):
        if self.state == tcstates.ASSIGNMENT:
            self.actions.append(token)
        elif self.state == tcstates.RETURN:
            self.actions.append(token)
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
        while True:
            try:
                if not self.reversed:
                    action = self.actions.pop(0)
                else:
                    action = self.actions.pop()
                try:
                    if action.GetValue() in self.methods.keys():
                        action = self.methods[action.GetValue()]
                except:
                    pass
                if not self.reversed:
                    param = self.params.pop(0).GetValue()
                else:
                    param = self.params.pop().GetValue()
                    
                if not self.basevar:
                    if not param: codes.append("%s" % (action))
                    else: codes.append("%s %s" % (action,param))
                else:
                    if not param:
                        codes.append("%s %s" % (action,self.basevar.GetValue()))
                    else:
                        codes.append("%s %s %s" % (action,self.basevar.GetValue(),param))
            except:
                break
        for line in codes:
            print line
            
            
            
            
            
            