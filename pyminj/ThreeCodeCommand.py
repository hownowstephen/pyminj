#!/usr/bin/python

class ThreeCodeCommand:
    
    def __init__(self,addr):
        self.address = addr
        
        self.param1 = None
        self.param2 = None
        self.method = None
        
        self.methods = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod", "&&": "and", "||": "or", "=": "assign"}
        self.compare = {"<": "lt", ">": "gt", "<=": "lte", ">=": "gte", "!=": "ne"}
    
    def SetParam(self,p):
        if self.param1 is None:
            self.param1 = p
            return False
        elif self.param2 is None:
            self.param2 = p
            return False
        else:
            return self
        
    def ResetParam2(self):
        self.param2 = None
        
    def SetMethod(self,m):
        if self.method:
            old = {'method':self.method,'param1':self.param1,'param2':self.param2}
        else:
            old = None
            
        if self.method == "if":
            if m in self.compare.keys():
                self.method = "%s_%s" % (self.method,self.compare[m])
                return
        
        try:
            self.method = self.methods[m]
        except:
            self.method = m
        return old
                
    def Print(self):
        print self.address,self.method,self.param1,self.param2
        
    def Encode(self,symboltable):
        p1,e = self.Resolve(self.param1,symboltable)
        p2,e = self.Resolve(self.param2,symboltable)
        if not e is None:
            for line in e: print line
        return "%s %s %s" % (self.method,p1,p2)
    
    def Resolve(self,param,symboltable):
        if param is None: return None,None
        try:
            return param.GetValue(),None
        except:
            try:
                if param['type'] == 'function':
                    return param['name'],None
                raise Exception
            except:
                return param['name'],None
                
                 