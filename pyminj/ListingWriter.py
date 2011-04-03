#!/usr/bin/python

import os.path as filepath

class ListingWriter:
    
    ''' Writes the listing of a file '''
    
    Listing = None
    OutputPath = 'output/%s.listing'
    Errors = []
    
    def __init__(self,file):
        ''' Opens the listing file for writing '''
        self.Listing = open(self.OutputPath % (filepath.basename(file)),'w')
        
    def WriteHeader(self,author,version):
        ''' Writes the header of the listing file, with author data etc '''
        self.Writeln("# Compiled by PyMinJ v%s" % (version['compiler']))
        self.Writeln("# Scanner Version: %s" % (version['scanner']))
        self.Writeln("# Parser Version: %s" % (version['parser']))
        self.Writeln("# @author %s" % author)
        self.Writeln('-------------------------------')
        
    def Write(self,string):
        '''Writes a plain string'''
        self.Listing.write(string)
        
    def Writeln(self,string):
        '''Writes a string and adds a newline'''
        self.Listing.write("%s\n" % string)
        
    def WriteError(self,type,message,line,char):
        '''Stores a new error to memory (for writing at the end) and writes it inline in the listing'''
        self.Errors.append({'type':type, 'line': line, 'char': char, 'message': message})
        error = self.Errors[-1]
        # Ignore non-line-specific errors
        if error['line'] < 0: return
        space = ''.join(' ' for x in range(0,error['char']+1))
        self.Writeln('%s^%s: %s\n' % (space,type,error['message']))
        
    def ParsingError(self,string,line,char):
        '''Thin wrapper that allows easier insertion of parsing errors'''
        self.WriteError('Parsing Error',string,line,char)
    
    def ScanningError(self,string,line,char):
        '''Thin wrapper that allows easier insertion of scanning errors'''
        self.WriteError('Scanning Error',string,line,char)
        
    def SymbolTableError(self,string,line,char):
        '''Thin wrapper that allows easier insertion of symbol table errors'''
        self.WriteError('Symbol Table Error',string,line,char)
        
    def WriteFooter(self):
        '''Writes the footer and a listing of errors to the listing'''
        self.Writeln('-------------------------------')
        self.Writeln('%i Errors reported' % len(self.Errors))
        for error in self.Errors:
            if error['line'] < 0:
                self.Writeln('\t %s: %s' % (error['type'],error['message']))
            else:
                self.Writeln('\t[Line %i, Char %i] \t%s: %s' % (error['line'],error['char'],error['type'],error['message']))

    