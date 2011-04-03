#!/usr/bin/env python

'''
@package pyminj
@class Token
@brief Represents a single token in MinJ code
@author Stephen Young (st_youn@encs.concordia.ca)
'''


class Token:

    Reserved = {'FLOW_CONTROL':['if','else','while','return'],
                'SYSTEM_IO':['System','in','out'],
                'DATA_TYPE':['int','char','void','class'],
                'FUNCTION':['main','new']}
    
    # Literal values that need to be translated to be understood by the parser
    Literals = {'IDENT':'i','NUMERIC':'n','CHARACTER_CONST':"c"}
    
    Value = None
    Type = None

    def __init__(self,type,value):
        self.Type = type.strip('<>')
        self.Value = value
        self.__reserved()

    def __reserved(self):
        '''Internal Function used to check if an identifier is more specifically a reserved word'''
        if self.Type == 'IDENT':
            for k,v in self.Reserved.iteritems():
                if self.Value in v:
                    self.Type = k
                    break

    def GetType(self):
        return self.Type

    def GetValue(self):
        return self.Value

    def SyntaxValue(self):
        if self.Type in self.Literals:
            return self.Literals[self.Type]
        return self.Value
    
    def __str__(self):
        return "<%s:%s>" % (self.Type,self.Value)

    def __nonzero__(self):
        return not (self.Type is None or self.Value is None)