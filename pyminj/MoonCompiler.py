'''
Compiler for translating PyMinJ intermediate code to the Moon virtual machine architecture
'''
import os,re
from copy import deepcopy

class MoonCompiler:
    '''
    MoonCompiler - Generates moon-compatible code from intermediate pyminj code
    using moon compatible commands
    '''
    
    # Define the path of the file to interpret
    __filepath__ = os.path.realpath(os.path.dirname(__file__)) + "/../output/intermediate.tmp"
    # Output file
    __outfile__ = None
    __symboltable = None
    __position = 0
    
    __global = None
    
    # A two dimensional list of intermediate level codes
    codes = []
    
    # Stores the resulting moon code
    __frames = []
    
    # Pre-emptive incrementation means we should start at zero
    Tmp = -1;
    Register = 5
    
    def __init__(self,out,symboltable):
        '''Load the current set of intermediate data and parse out the lines to be converted to Moon commands'''
        file = open(self.__filepath__,'r')
        lines = file.readlines()
        for line in lines:
            if not line.startswith("#"):
                code = line.strip().split(' ')
                if len(code) > 3 or code[0] == '': continue
                self.codes.append(code)
        self.__outfile__ = out;
        self.__symboltable = symboltable
        self.CurrMethod = None
    
    def Compile(self):
        '''Perform the compilation using the generated symboltable'''
        #print self.__symboltable
        
        self.__global = MoonMethod('global',{},self.__position)
        
        for key,element in self.__symboltable['global'].iteritems():
            if element['type'] == 'identifier':
                if element['datatype'] == 'int':
                    self.__global.AddOp("res",[32],key)
                else:
                    self.__global.AddOp("res",[8],key)
        
        for line in self.codes:
            command = line[0]
            try:    base = line[1]
            except: base = ''
            try:    param = line[2]
            except: param = ''
            method = "Handle%s" % command.capitalize()
            #if self.CurrMethod: self.CurrMethod.AddOp("ORIG: %s %s %s" % (command,base,param))
            if hasattr(self,method):
                _method = getattr(self,method)
                _method(base,param)
            else:
                print "No handler configured for %s" % command
    
    def GetReg(self):
        '''Retrieve the next available volatile register (round robin to allow for maximized access)'''
        self.Register += 1
        if self.Register > 15:
            self.Register = 6
        return "r%i" % self.Register
    
    def GetTmp(self):
        '''Retrieve the next temporary variable, variously used to store constant data and implicit vars'''
        self.Tmp += 1
        return "t%i" % self.Tmp;
    
    def GetType(self,var):
        if var == "return":
            datatype =  self.__symboltable['global'][self.CurrMethod.Name]['datatype']
        else:
            try:
                datatype = self.__symboltable[self.CurrMethod.Name][var]['datatype']
            except:
                # Try a member variable
                try:
                    datatype =  self.__symboltable['global'][var]['datatype']
                # Try a param
                except:
                    pc = 0
                    for param in self.__symboltable['global'][self.CurrMethod.Name]['params']:
                        if param['name'] == var:
                            datatype = param['datatype']
                            var = "%s_p%i" % (self.CurrMethod.Name,pc)
                            break
                        pc += 1
        if datatype == "int":
            return "w",var
        elif datatype == "char":
            return "b",var
        else:
            return False
            
    def HandleAdd(self,base,param):
        pass
    
    def HandleAdvance(self,base,param):
        pass
    
    def HandleAssign(self,base,param):
        '''Handle assignment method'''
        if param == "system.in":
            self.CurrMethod.AddOp("getc",[base])
        else:
            type = self.Immediate(param)
            if type:
                reg = self.LoadLiteral(type,param,base)
                self.CurrMethod.AddOp("s%s" % type,["%s(r0)" % base,reg])
            else:
                type,param = self.GetType(param)
                reg = self.GetReg()
                self.CurrMethod.AddOp("l%s" % type,[reg,"%s(r0)" % param])
                self.CurrMethod.AddOp("s%s" % type,["%s_rt(r0)" % self.CurrMethod.Name,reg])
    
    def HandleBfalse(self,base,param):
        pass
    
    def HandleBtrue(self,base,param):
        pass
    
    def HandleGt(self,base,param):
        pass
    
    def HandleLte(self,base,param):
        pass
    
    def HandleMethod(self,base,param):
        if param == "start":
            self.OpenMethod(base)
        elif param == "end":
            self.CloseMethod()
        
    def HandlePointer(self,base,param):
        pass
    
    def HandlePrint(self,base,param):
        if base == 'stdout':
            reg = self.GetReg()
            type = self.Immediate(param)
            if type: 
                reg = self.LoadLiteral(type,param,base)
            else:
                self.CurrMethod.AddOp("lb",[reg,"%s(r0)" % param])
            self.CurrMethod.AddOp("putc",[reg])
                
        else:
            # Will never be reached under PyMinJ v1.0
            pass
    
    def HandleReturn(self,base,param):
        pass
    
    def Immediate(self,item):
        '''Tests if the value supplied is an immediate identifier - a direct char or integer'''
        # Checks for integer
        try:
            float(item)
            return "w"
        except:
            pass
        #checks for char
        if re.match("'.'",item): return "b"
        return False
    
    def LoadLiteral(self,type,param,base):
        var = self.GetTmp()
        vol = self.GetReg() # Retrieve a volatile register to use
        self.__global.AddOp("d%s" % type,[param.replace("'",'"'),13,10,0],var)
        self.CurrMethod.AddOp("l%s" % type,[vol,"%s(r0)" % var])
        return vol
    
    def OpenMethod(self,methodname):
        '''Open up the method'''
        signature = self.__symboltable['global'][methodname]
        frametop = self.__position
        self.CurrMethod = MoonMethod(methodname,signature,frametop)
        self.CurrMethod.LabelNext = methodname
        if methodname == 'main':
            self.CurrMethod.AddOp("align")
            self.CurrMethod.AddOp("entry")
        else:
            self.CurrMethod.AddOp("nop")
        
    def CloseMethod(self):
        if self.CurrMethod.Name == 'main': self.CurrMethod.AddOp("hlt")
        self.__frames.append(self.CurrMethod)
        self.CurrMethod = None
    
    def PrintIntermediate(self):
        for code in self.codes:
            print code
    
    def WriteMFile(self):
        self.__global.Write()
        for method in self.__frames:
            method.Write()
            
class MoonMethod:
    '''
    MoonMethod - Represents a single method of Pyminj code as interpreted into a Moon frame
    '''
    
    def __init__(self,name,signature,top):
        '''Takes a label name and a signature, which is the method signature for the given method'''
        self.Name = name
        self.__signature = signature
        self.Top = top
        self.__operations__ = []
        self.LabelNext = None
    
    def AddOp(self,opcode,params=[],varname=''):
        '''Add the operation to the list of operations'''
        if self.LabelNext:
            varname = self.LabelNext
            self.LabelNext = None
        op = [varname,opcode]
        if params: op.append(','.join(map(str,params)))
        self.__operations__.append(op)
        
    def GetSize(self,type):
        if type == 'int': return 32
        else: return 8
    
    def Write(self):
        pc = 0
        try:
            header = MoonMethod(None,[],None)
            header.AddOp('res',[self.GetSize(self.__signature['datatype'])],'%s_rt' % self.Name)
            for param in self.__signature['params']:
                if param['datatype'] == 'int':
                    header.AddOp('res',[32],'%s_p%i' % (self.Name,pc))
                else:
                    header.AddOp('res',[8],'%s_p%i' % (self.Name,pc))
                pc += 1
            header.Write()
        except:
            pass
        
        '''Write the method to the supplied file handle'''
        for op in self.__operations__:
            # Write to a tmp file
            file = open("tmp.m","a")
            file.write("%s\n" % "\t".join(op))
            file.close()
            
if __name__ == "__main__":
    # Wipe the file
    file = open("tmp.m","w")
    file.close()
    symboltable = {'global':{'x':{'datatype': 'int', 'type': 'identifier', 'name': 'x'}, 
                             'main':{'datatype': 'void', 'type': 'function', 'name': 'main'},
                             'y':{'datatype': 'char', 'type': 'identifier', 'name': 'y'},
                             'printchars': {'datatype': 'int', 'type': 'function', 'name': 'printchars'},
                             'inc': {'datatype': 'int', 'params': [{'datatype': 'int', 'name': 'value'}], 'type': 'function', 'name': 'inc'}}
                  }
    compiler = MoonCompiler("output.mc",symboltable)
    compiler.Compile()
    compiler.WriteMFile()
    # Temporarily auto-run the file
    os.system("moon tmp.m;cat tmp.m")