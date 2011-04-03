#!/usr/bin/env python

'''
Errors.py
@package pyminj
@brief Contains all the errors thrown by various stages of the compilation process
@author Stephen Young (st_youn@encs.concordia.ca)
'''

class InvalidTokenException(Exception):
    '''Handler for the scanner invalid token exceptions'''
    def __init__(self,value='Token not recognized'):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
    
class SyntaxException(Exception):
    '''Handler for parser syntax exceptions'''
    def __init__(self,value='Syntax is not correct'): 
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class MissingTokenException(Exception):
    '''Handler for parser missing token exceptions'''
    def __init__(self,value='A token is missing'): 
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class IdentifierExistsException(Exception):
    '''Handler for undeclared identifiers'''
    def __init__(self,value='The identifier already exists'): 
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class IdentifierUndeclaredException(Exception):
    '''Handler for undeclared identifiers'''
    def __init__(self,value='The identifier requested has not been declared'): 
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class IdentifierUninitializedException(Exception):
    '''Handler for uninitialized identifiers'''
    def __init__(self,value='The identifier requested has not been declared'): 
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class FunctionDoesNotExistException(Exception):
    '''Handler for non-existant functions'''
    def __init__(self,value='The function being called does not exist'): 
        self.value = value
    def __str__(self):
        return repr(self.value)