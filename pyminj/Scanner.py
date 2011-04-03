#!/usr/bin/env python

'''
@package PyMinJ
@class Scanner
@brief Manages the tokenizing of MinJ code as specified by the accompanying language documentation
@note All documentation can be found in /doc/
@author Stephen Young (stephen.t.young@gmail.com)
'''

from SimpleDFA import SimpleDFA
from Token import Token
from Errors import InvalidTokenException

class Scanner:
    """@class Scanner"""

    Version = "1.1.2"
    Author = "st_youn"

    Whitespace = [' ','\n','\t',None]
    SourceFile = None
    CurrChar = False
    # For managing the output
    Listing = None
    Line = 0
    Char = 0
    CurrLine = ' 0| '
    Errors = []


    def __init__(self,file,listing,conf='conf/tokens.dfa'):
        #  Load Source
        self.SourceFile = open(file,'r')
        # Set some internal initial vars
        self.Errors = []
        self.Line = 0
        self.Char = 0
        # Create a new DFA object
        self.DFA = SimpleDFA()
        # Load data into the DFA
        self.DFA.Load(conf)
        
        # Set the listing writer
        self.Listing = listing
        '''self.Listing = open(self.OutputPath % (filepath.basename(file)),'w')
        self.Listing.write("# Compiled by PyMinJ v%s\n# @author %s\n" % (self.Version,self.Author))
        self.Listing.write('-------------------------------\n\n')'''

    def WriteLine(self):
        self.Listing.Writeln(self.CurrLine.strip("\n"))
        self.CurrLine = ''

    def WriteError(self):
        error = self.Errors[-1]
        space = ''.join(' ' for x in range(0,error['char']+1))
        self.Listing.Write('%s^Scanner Error: %s\n\n' % (space,error['type']))

    def WriteLast(self):
        self.WriteLine()
        self.Listing.Write('\n\n-------------------------------\n')
        self.Listing.Write('%i Errors reported by scanner\n' % len(self.Errors))
        for error in self.Errors:
            self.Listing.Write('\tLine %i, Char %i:\t' % (error['line'],error['char']) + error['type'] + '\n')

    def SkipBlanks(self):
        comment = False
        nextchar=self.CurrChar
        while True:
            if nextchar == '#':
                comment = True
            if nextchar == '\n':
                comment = False
            if (not nextchar in self.Whitespace and not comment) or not nextchar:
                break
            nextchar = self.GetChar()
        return nextchar

    def SkipLine(self):
        while True:
            self.CurrChar = self.GetChar()
            if self.CurrChar == '\n' or self.CurrChar is None: return

    def TokenError(self,message,line=None,char=None):
        
        if not line: line = self.Line
        if not char: char = self.Char
        
        self.SkipLine()
        self.Listing.ScanningError("Unrecognized Token", line, char)

        self.CurrChar = self.SkipBlanks()
        # Finally throw an error
        raise InvalidTokenException()

    def NextToken(self):
        '''The main driving function of the scanner, performs the task of retrieving and returning the next qualified token to the compiler'''
        token = ''
        while True:
            # Check that we have loaded a character, or load one
            if self.CurrChar == False: self.CurrChar = self.GetChar()

            # Check for erroneous tokens
            if (self.CurrChar and not self.DFA.Next(self.CurrChar) and self.DFA.StateNum() == 0):
                self.TokenError('Invalid token "%s"' % self.CurrChar,self.Line, self.Char+1)

            # Check for unterminated tokens
            if(self.CurrChar and not self.DFA.Next(self.CurrChar) and not self.DFA.Check()):
                self.TokenError('Unterminated token',self.Line,self.Char)

            # Check if we can do a transition
            if (not self.CurrChar in self.Whitespace) and self.DFA.Next(self.CurrChar):
                # Perform actual transition
                self.DFA.Advance(self.CurrChar)
                # Update the token
                token = "%s%s" % (token,self.CurrChar)
            # If no legal transition exists, we must have completed the token
            else:
                # If there is no token supplied, we're at the end so we need to tie it up
                if token == '':
                    token = None
                    #sself.WriteLast()
                # Otherwise we create a token object to pass back to the compiler
                tk = Token(self.DFA.State(),token)
                # Reset the DFA for parsing the next token
                self.DFA.Reset()
                # Skip any following blank characters
                self.CurrChar = self.SkipBlanks()
                return tk
            # If we've read the whole file, break
            if not self.CurrChar: break
            # Load the next character
            self.CurrChar = self.GetChar()
        return False

    def GetChar(self):
        nextchar = self.SourceFile.read(1)
        self.CurrLine = "%s%s" % (self.CurrLine,nextchar)
        if nextchar == '\n':
            self.WriteLine()
            self.Line += 1
            self.Char = 0
            if(self.Line < 10):
                self.CurrLine = ' %i| ' % self.Line
            else:
                self.CurrLine = '%i| ' % self.Line
        self.Char += 1
        if not nextchar: return None
        return nextchar
    
    def GetVersion(self):
        return "%s (%s)" % (self.Version, self.Author)
