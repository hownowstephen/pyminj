import string,sys
from Token import Token
from collections import deque

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

TEMPVAR = 0
NESTLEVEL = 0
whileLoops = {}

class ThreeCodeGenerator:
    ''' Performs the translation of code blocks into three code intermediate expressions'''
    methods = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod", 
               "&&": "and", "||": "or", "=": "assign","<": "lt", ">": "gt", 
               "<=": "lte", ">=": "gte", "!=": "ne", "==": "eq"}
    def __init__(self,symboltable,tokenset,context,file):
        ''' Initialize data needed'''
        self.symbols = symboltable
        self.tokens = deque(tokenset)
        self.output = []
        self.state = tcstates.INIT;
        self.reversed = False
        self.outputfile = file
        
        self.basevar = None
        self.actions = []
        self.params = []
        
        self.codes = []
        self.currOperator = None
        self.subscripting = False
        self.lastvar = None
        self.stash = []
        
    def AddCode(self,param,operator=None,base=None,staging=False):
        '''Generates a three-code of the form <operator> <base> <param>'''
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
        
        if param is None: param = ""
        # If we're not saving these for later
        code = "%s %s %s" % (op,b,param)
        if not staging and op:
            self.codes.append(code)
        else:
            return code
    
    def IncTmp(self):
        '''Increment our looping counter for the temp variables'''
        global TEMPVAR
        TEMPVAR += 1;
        if TEMPVAR > 12:
            TEMPVAR = 0 
        return "tmp%i" % TEMPVAR   
        
    def GetToken(self):
        '''Retrieve a token from the beginning of the list'''
        return self.tokens.popleft()
    
    def GetMethod(self,token):
        '''Resolve a token into a method using the methods dict'''
        if token.GetValue() in self.methods:
            return self.methods[token.GetValue()]
        else:
            return token.GetValue()
            
    def Parse(self,construct=True):
        '''
        Parse function, performs initial dispatch. Calls itself recursively until
        no tokens remain. Subfunctions are called based on the input token type
        '''
        try:
            token = self.GetToken()
            # Convert the token type to a nice camelcase handler method name
            method = "Handle%s" %  string.capwords(token.GetType(),'_').replace("_","")
            try:
                function=getattr(self,method) 
                function(token)
                self.Parse()
            except:
                #print sys.exc_info()
                pass
        except:
            #print sys.exc_info()
            # No more tokens exist - unless instructed not to, we can output the 
            # intermediate code
            if construct: return self.ConstructCodes()       
    
    def HandleAssign(self,token):
        '''Handler for assignment tokens'''
        self.currOperator = token
        self.state = tcstates.ASSIGNMENT
        
    def HandleCharacterConst(self,token):
        '''Handler for character constant tokens'''
        if self.state in [tcstates.RETURN,tcstates.RETURN2,tcstates.ASSIGNMENT]:
            self.AddCode(token)
            self.currOperator = None
        elif self.state == tcstates.SYSTEMOUT:
            self.AddCode(token,'print','stdout')
            
    def HandleCompare(self,token):
        '''Handler for comparison tokens'''
        self.currOperator = token
        
    def HandleCompare2(self,token):
        '''Handler for second-tier comparison tokens'''
        self.currOperator = token
            
    def HandleDataType(self,token):
        '''Handler for input data types'''
        if self.state == tcstates.SYSTEMIN:
            self.AddCode("system.in")
            
    def HandleDelimiter(self,token):
        '''Handler for delimiters'''
        if self.state == tcstates.INIT:
            pass
        # elif self.state == tcstates.ASSIGNMENT and token.GetValue() == "[":
        #    self.subscripting = True
        #    subscript = self.GetToken()
        #     tmp = self.IncTmp()
        #     self.AddCode(self.lastvar,"pointer",tmp)
            
    def HandleFlowControl(self,token):
        '''Handler for flow control tokens (conditions, returns etc)'''
        global NESTLEVEL
        value = token.GetValue()
        if self.state == tcstates.INIT:
            if value != "return":
                # Handle other flow control
                if value == "if": 
                    self.state = tcstates.IF
                    NESTLEVEL += 1
                elif value == "while": 
                    self.state = tcstates.WHILE
                    NESTLEVEL += 1
                    self.AddCode(None,"label","while%i" % NESTLEVEL)
                elif value == "endif":
                    pass
                elif value == "endelse":
                    self.AddCode(None,"label","endif%i" % NESTLEVEL)
                    NESTLEVEL -= 1
                elif value == "endwhile":
                    global whileLoops
                    target = "while%i" % NESTLEVEL
                    for code in whileLoops[target]:
                        self.codes.append(code)
                    NESTLEVEL -= 1
                elif value == "else":
                    self.state = tcstates.ELSE
                    self.AddCode(None,"goto","endif%i" % NESTLEVEL)
                    self.AddCode(None,"label","else%i" % NESTLEVEL)
            else:
                self.state = tcstates.RETURN
                self.basevar = Token("IDENT","return")
                self.currOperator = Token("OPERATOR","=")
            #self.state = tcstates.RETURN
    def HandleFunction(self,token):
        '''Handler for function tokens'''
        raise Exception        
    
    def HandleIdent(self,token):
        '''Check if we should be converting to a subscript'''
        next = self.GetToken()
        if next.GetValue() == '[':
            ss = self.GetToken()
            tmp = self.IncTmp()
            self.AddCode(token,"pointer",tmp)
            self.AddCode(ss,"advance",tmp)
            token = tmp
        else:
            self.tokens.appendleft(next)
        
        
        self.lastvar = token
        '''Handler for identifiers'''
        if self.state == tcstates.INIT:
            self.basevar = token
            self.state = tcstates.IDENT
            
            
        # Check for assignment state or return state
        elif self.state in [tcstates.ASSIGNMENT,tcstates.RETURN,tcstates.RETURN2,tcstates.IF,tcstates.WHILE]:
            
            # Check if we are just starting the return
            if self.state == tcstates.RETURN:
                self.AddCode(token)
                self.state = tcstates.RETURN2
            
            # Check if we have completed an if statement
            if self.state == tcstates.IF:
                if self.basevar:
                    self.GenerateCondition(token)    
            elif self.state == tcstates.WHILE:
                if self.basevar:
                    self.GenerateWhile(token)
            
            # Check if we need to set the basevar
            if not self.basevar:
                self.basevar = token

            try:
                # Lookahead for next token
                next = self.GetToken()
                # Operators passed to the operator handler
                if next.GetType() == "OPERATOR":
                    self.HandleOperator(next)
                # Handle embedded function calls
                elif next.GetType() == "DELIMITER" and next.GetValue() == "(":
                    target = self.CallFunction(token.GetValue())
                    if not self.currOperator is None:
                        self.AddCode(target)
                        self.currOperator = None
                else:
                    if self.state in [tcstates.ASSIGNMENT]:
                        if self.basevar:
                            self.AddCode(token)
                            self.currOperator = None
                    # Push back to be handled by the parser
                    self.tokens.appendleft(next)
            except:
                pass
        # Check if we are writing the variable to stdout
        elif self.state == tcstates.SYSTEMOUT:
            self.AddCode(token,'print','stdout')
        
    def CallFunction(self,fn):
        '''Generates the codes necessary to call a given user-defined function'''
        param = 1
        while True:
            try:
                token = self.GetToken()
                if token.GetType() == "DELIMITER":
                    # end of the loop
                    if token.GetValue() == ")": break
                    # Ignore commas
                    elif token.GetValue() == ",": continue
                self.codes.append("assign %s_p%i %s" % (fn,param,token.GetValue()))
                param = param + 1
            except:
                break
        # Get a new temporary variable to store results in
        target = self.IncTmp()
        self.codes.append("assign %s_return %s" % (fn,target))
        self.codes.append("call %s" % fn)
        return target
        
        
            
    def HandleNumeric(self,token):
        '''Handler for numeric tokens'''
        if self.state in [tcstates.RETURN,tcstates.RETURN2,tcstates.ASSIGNMENT]:
            self.AddCode(token)
            self.currOperator = None
        elif self.state == tcstates.SYSTEMOUT:
            self.AddCode(token,'print','stdout')
        elif self.state == tcstates.IF:
            if self.basevar: 
                self.GenerateCondition(token)
        elif self.state == tcstates.WHILE:
            if self.basevar:
                self.GenerateWhile(token)
        elif self.state == tcstates.IDENT:
            tmp = self.IncTmp()
            self.AddCode(self.basevar,"pointer",tmp)
            self.AddCode(token,"advance",tmp)
            self.basevar = tmp
    
    def GenerateCondition(self,token):
        '''Generator for condition block codes'''
        global NESTLEVEL
        tmp = self.IncTmp()
        self.AddCode(self.basevar,Token("ASSIGN","="),tmp)
        self.AddCode(token,self.currOperator,tmp)
        self.AddCode("else%i" % NESTLEVEL,"branch_false",tmp);
        
    def GenerateWhile(self,token):
        '''Generator for condition block codes'''
        global NESTLEVEL,whileLoops
        tmp = self.IncTmp()
        target = "while%i" % NESTLEVEL
        whileLoops[target] = []
        whileLoops[target].append(self.AddCode(self.basevar,Token("ASSIGN","="),tmp,True))
        whileLoops[target].append(self.AddCode(token,self.currOperator,tmp,True))
        whileLoops[target].append(self.AddCode(target,"branch_true",tmp,True))
        
        
    def HandleOperator(self,token):
        '''Handler for operators'''
        self.currOperator = token
        
    def HandleOpMinus(self,token):
        '''Handler for minus operation'''
        self.currOperator = token
    
    def HandleSystemIo(self,token):
        '''Handler for IO statements'''
        if self.state == tcstates.ASSIGNMENT:
            self.state = tcstates.SYSTEMIN
        elif self.state == tcstates.INIT:
            self.state = tcstates.SYSTEMOUT
            
            
    def ConstructCodes(self):
        '''Output function, prints the code to file'''
        if self.state == tcstates.RETURN2:
            self.AddCode(None,"return",None)
        for code in self.codes:
            self.outputfile.write("%s\n"% code)
            
            
            
            
            
            