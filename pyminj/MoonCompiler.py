'''
Compiler for translating PyMinJ intermediate code to the Moon virtual machine architecture
'''
import os,re,sys

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
    Register = 4
    
    def __init__(self,out,symboltable):
        '''Load the current set of intermediate data and parse out the lines to be converted to Moon commands'''
        file = open(self.__filepath__,'r')
        lines = file.readlines()
        for line in lines:
            # Ignore commented code
            if not line.startswith("#"):
                code = line.strip().split(' ')
                # Ignore invalid code / empty lines
                if len(code) > 3 or code[0] == '': continue
                self.codes.append(code)
        # Configure what file we will write to
        self.__outfile__ = out;
        file = open(self.__outfile__,"w")
        file.close()
        # Configure the symboltable
        self.__symboltable = symboltable
        # Empty out the currmethod
        self.CurrMethod = None
    
    def Compile(self):
        '''Perform the compilation using the generated symboltable'''
        #print self.__symboltable
        
        self.__global = MoonMethod('global',{},self.__position)
        
        # Handle all the initial global elements that need to be defined
        for key,element in self.__symboltable['global'].iteritems():
            if element['type'] == 'identifier':
                if element['datatype'] == 'int':
                    self.__global.AddOp("res",[32],key)
                else:
                    self.__global.AddOp("res",[8],key)
        
        # Iterate over all the code
        for line in self.codes:
            command = line[0]
            try:    base = line[1]
            except: base = ''
            try:    param = line[2]
            except: param = ''
            # Generate the variable method to call
            method = "Handle%s" % command.capitalize()
            #if self.CurrMethod: self.CurrMethod.AddOp("ORIG: %s %s %s" % (command,base,param))
            if hasattr(self,method):
                _method = getattr(self,method)
                _method(base,param)
            else:
                # Failsafe for unknown operations
                print "No handler configured for %s" % command
    
    def GetReg(self):
        '''Retrieve the next available volatile register (round robin to allow for maximized access)'''
        # Increment the current register
        self.Register += 1
        # Cap at 16 registers (limit in the moon VM)
        if self.Register > 14:
            self.Register = 5
        return "r%i" % self.Register
    
    def GetTmp(self):
        '''Retrieve the next temporary variable, variously used to store constant data and implicit vars'''
        self.Tmp += 1
        return "t%i" % self.Tmp;
    
    def GetType(self,var):
        '''Determines the type of a variable and provides the size (b)yte or (w)ord, as well as any mutations to the var'''
        datatype = False
        # Work out what is meant by 'return'
        if var == "return":
            datatype =  self.__symboltable['global'][self.CurrMethod.Name]['datatype']
            var = "%s_rt" % (self.CurrMethod.Name)
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
                    try:
                        for param in self.__symboltable['global'][self.CurrMethod.Name]['params']:
                            if param['name'] == var:
                                datatype = param['datatype']
                                var = "%s_p%i" % (self.CurrMethod.Name,pc)
                                break
                            pc += 1
                    # Some special cases (mutated and temporary variables)
                    except:
                        pmatch = re.match("(?P<method>[\w\$_]+)_p(?P<param>\d+)",var)
                        rmatch = re.match("(?P<method>[\w\$_]+)_rt",var)
                        if pmatch:
                            # Pull out the method and param number 
                            method = pmatch.group("method")
                            pnum = int(pmatch.group("param"))
                            datatype = self.__symboltable['global'][method]['params'][pnum]['datatype']
                        elif rmatch:
                            # Pull out the return value details
                            method = rmatch.group("method")
                            datatype = self.__symboltable['global'][method]['datatype']
        # Finally work out whether we are working with a byte or a word, and return the updated details
        if datatype == "int":
            return "w",var
        elif datatype == "char":
            return "b",var
        else:
            return False,var
            
    def HandleAdd(self,base,param):
        self.HandleMath(base,param,"add")
    
    def HandleMul(self,base,param):
        self.HandleMath(base,param,"mul")
    
    def HandleSub(self,base,param):
        self.HandleMath(base,param,"sub")
        
    def HandleMod(self,base,param):
        self.HandleMath(base,param,"mod")
    
    def HandleMath(self,base,param,opbase):
        '''Handler for the add operation'''
        reg = self.GetReg()
        type,base = self.GetType(base)
        self.CurrMethod.AddOp("l%s" % type,[reg,"%s(r0)" % base])
        # If we are adding a direct param to the var, use addi
        if self.Immediate(param): op = "%si" % opbase
        else: op = opbase
        self.CurrMethod.AddOp(op,[reg,reg,param])
        self.CurrMethod.AddOp("s%s" % type,["%s(r0)" % base,reg])
            
    
    def HandleAdvance(self,base,param):
        pass
    
    def HandleAssign(self,base,param):
        '''Handle assignment method'''
        rmatch = re.match("tmp(?P<id>\d+)",base)
        if param == "system.in":
            reg = self.GetReg()
            type,base = self.GetType(base)
            self.CurrMethod.AddOp("getc",[reg])
            self.CurrMethod.AddOp("s%s" % type,["%s(r0)" % base,reg])
        elif rmatch:
            reg = "r%s" % rmatch.group('id')
            type,param = self.GetType(param)
            self.CurrMethod.AddOp("l%s" % type,[reg,"%s(r0)" % param])
        else:
            type = self.Immediate(param)
            if type:
                reg = self.LoadLiteral(type,param,base)
                btype,base = self.GetType(base)
                self.CurrMethod.AddOp("s%s" % type,["%s(r0)" % base,reg])
            else:
                type,param = self.GetType(param)
                btype,base = self.GetType(base)
                reg = self.GetReg()
                # Load the value of the assignment variable
                self.CurrMethod.AddOp("l%s" % type,[reg,"%s(r0)" % param])
                # Store it in the value of the assignee
                self.CurrMethod.AddOp("s%s" % type,["%s(r0)" % base,reg])
    
    # These are thinly wrapped usages of the HandleBranch method
    # Which can be found underneath
    
    def HandleEq(self,base,param):
        ''' Handle '==' '''
        self.HandleCond(base,param,'eq')
    
    def HandleGt(self,base,param):
        ''' Handle '>' '''
        self.HandleCond(base,param,'gt',False)
        
    def HandleGte(self,base,param):
        ''' Handle '>=' '''
        self.HandleCond(base,param,'ge')

    def HandleLt(self,base,param):
        ''' Handle '<' '''
        self.HandleCond(base,param,'lt')
        
    def HandleLte(self,base,param):
        ''' Handle '<=' '''
        self.HandleCond(base,param,'le')
        
    def HandleNe(self,base,param):
        ''' Handle '!=' '''
        self.HandleCond(base,param,'ne')
    
    def HandleCond(self,base,param,brtype,zero=True):
        '''Acts as a wrapper for the template used to generated conditional branching commands'''
        rmatch = re.match("tmp(?P<id>\d+)",base)
        if rmatch:
            reg = "r%s" % rmatch.group('id')
            type,param = self.GetType(param)
            # Perform test
            self.CurrMethod.AddOp("c%si" % brtype,[reg,reg,param])
            
    def HandleBfalse(self,base,param):
        rmatch = re.match("tmp(?P<id>\d+)",base)
        if rmatch:
            reg = "r%s" % rmatch.group('id')
            self.CurrMethod.AddOp("bnz",[reg,param])
            
    def HandleBtrue(self,base,param):
        rmatch = re.match("tmp(?P<id>\d+)",base)
        if rmatch:
            reg = "r%s" % rmatch.group('id')
            self.CurrMethod.AddOp("bz",[reg,param])
    
    def HandleCall(self,base,param):
        self.CurrMethod.AddOp("jl",['r15',base])
    
    def HandleGoto(self,base,param):
        self.CurrMethod.AddOp('j',[base])
        self.CurrMethod.LabelNext = param
    
    def HandleLabel(self,base,param):
        self.CurrMethod.LabelNext = base
        self.CurrMethod.AddOp("nop")
    
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
                type,param = self.GetType(param)
                self.CurrMethod.AddOp("lb",[reg,"%s(r0)" % param])
            if type == "b":
                self.CurrMethod.AddOp("putc",[reg])
            else:
                type,param = self.GetType(param)
                self.CurrMethod.AddOp("lw",['r1',"%s(r0)" % param])
                self.CurrMethod.AddOp("jl",['r15','putint'])
                
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
        '''Wrapper for the functionality of loading raw data (a char or int) into a variable'''
        var = self.GetTmp()
        vol = self.GetReg() # Retrieve a volatile register to use
        self.__global.AddOp("d%s" % type,[param.replace("'",'"'),13,10,0],var)
        self.CurrMethod.AddOp("l%s" % type,[vol,"%s(r0)" % var])
        return vol
    
    def OpenMethod(self,methodname):
        '''Open up a method block'''
        # PUll the method signature out of the global symbol definition
        signature = self.__symboltable['global'][methodname]
        signature['internals'] = {}
        for name,line in self.__symboltable[methodname].iteritems():
            signature['internals'][name] = line
        frametop = self.__position
        # Generate a new CurrentMethod container
        self.CurrMethod = MoonMethod(methodname,signature,frametop)
        self.CurrMethod.LabelNext = methodname
        # Perform some preliminary insertions
        if methodname == 'main':
            self.CurrMethod.AddOp("align")
            self.CurrMethod.AddOp("entry")
        else:
            # To ensure that we don't clash with any other name inputs, add in a nop
            self.CurrMethod.AddOp("nop")
        
    def CloseMethod(self):
        '''Terminates the current method block'''
        if self.CurrMethod.Name == 'main': self.CurrMethod.AddOp("hlt")
        else: self.CurrMethod.AddOp("jr",['r15'])
        self.__frames.append(self.CurrMethod)
        self.CurrMethod = None
    
    def PrintIntermediate(self):
        '''Debug function, allows printing of all intermediate code'''
        for code in self.codes:
            print code
    
    def WriteMFile(self):
        '''Performs the writing of the output file'''
        target = open(self.__outfile__,'w');
        self.__global.Write(target)
        for method in self.__frames:
            method.Write(target)
            
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
    
    def Write(self,file):
        pc = 0
        try:
            header = MoonMethod(None,[],None)
            # Allocate space for the return value
            header.AddOp('res',[self.GetSize(self.__signature['datatype'])],'%s_rt' % self.Name)
            # Loop through and add in the required allocation blocks for the signature vars
            for param in self.__signature['params']:
                if param['datatype'] == 'int':
                    header.AddOp('res',[32],'%s_p%i' % (self.Name,pc))
                else:
                    header.AddOp('res',[8],'%s_p%i' % (self.Name,pc))
                pc += 1
            for key,var in self.__signature['internals'].iteritems():
                if var['datatype'] == 'int':
                    header.AddOp('res',[32],'%s' % (var['name']))
                else:
                    header.AddOp('res',[8],'%s' % (var['name']))    
            
            header.Write(file)
        except:
            print sys.exc_info()
            if self.Name == "main":
                header = MoonMethod(None,[],None)
                header.AddOp('res',[32],"main_rt")
                header.Write(file)
        
        '''Write the method to the supplied file handle'''
        for op in self.__operations__:
            # Write to the output file
            file.write("%s\n" % "\t".join(op))
            
if __name__ == "__main__":
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
    os.system("moon /home/stephen/school/comp442/PyMinJ/moon/newlib.m tmp.m;cat tmp.m")