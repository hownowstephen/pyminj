#!/usr/bin/python

class ThreeCodeCommand:
    
    def __init__(self,addr):
        self.address = addr
        
        self.params = []
        self.method = []
        
        self.methods = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod", "&&": "and", "||": "or", "=": "assign"}
        self.compare = {"<": "lt", ">": "gt", "<=": "lte", ">=": "gte", "!=": "ne"}
    
    def SetParam(self,p):
        self.params.append(p)
        
    def SetMethod(self,m):  
        try:
            if self.method[-1] == "if":
                if m in self.compare.keys():
                    self.method[-1] = ("%s_%s" % (self.method[-1],self.compare[m]))
                    return
        except:
            pass
        
        try:
            self.method.append(self.methods[m])
        except:
            self.method.append(m)
                
    def Print(self):
        print self.address,self.method,self.param1,self.param2
        
    def Encode(self,symboltable):
        #print "PARAMS: ",self.params
        try: p1 = self.Resolve(self.params.pop(0),symboltable)
        except: p1 = None
        out = None
        e = []
        method = self.method.pop()
        while True:
            try:
                param = self.params.pop()
                try:
                    if param['type'] == 'function':
                        pass
                    raise Exception
                except:
                    p2 = self.Resolve(param,symboltable)
            except:
                p2 = None
            code = "%s %s %s" % (method ,p1,p2)
            if not out: out = code
            else: e.append(code)
            if not self.params: break
            print "PARMS",self.params
            method = self.method.pop()
        return out,e
    
    def Resolve(self,param,symboltable):
        if param is None: return None
        try:
            return param.GetValue()
        except:
            try:
                if param['type'] == 'function':
                    return param['name']
                raise Exception
            except:
                return param['name']
                
                 