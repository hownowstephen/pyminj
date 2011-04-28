#!/usr/bin/python
import sys
import os.path as filepath
from pyminj import *

Version = '0.8.1'
Author = 'Stephen Young (st_youn@encs.concordia.ca)'

try:
    fname = sys.argv[1]
except:
    print "No source file specified!"
    sys.exit(1)

# Define what programs are the test cases
tests = ['class.multierr.mj','class.noerr.mj', 'inline.err.mj','inline.noerr.mj','nonsense.noerr.mj']

# Load a parser
parser = Parser('conf/syntax.ll1')

# Load a listing generator
listing = ListingWriter(fname)

# Load a scanner for the file
scanner = Scanner(fname,listing)

# Load a generator with a reference to the parser's symbol table
generator = IntermediateGenerator(parser.symboltable)
parser.SetIntermediateCodeGenerator(generator)

# Write the listing header
listing.WriteHeader(Author, {'compiler':Version,'scanner':scanner.GetVersion(),'parser':parser.GetVersion()})

# Loop through all the tokens and handle them with the parser
while True:
    
    # Read a new token, or handle invalid tokens
    try:
        token = scanner.NextToken()
    except:
        print "Invalid token found"
        continue;
    
    # If the token is False, we are done parsing, so we cleanup and finish listing
    if not token:
        parser.symboltable.Print()
        try:
            parser.CheckStack()
        except MissingTokenException as e:
            listing.ParsingError(e.__str__(),-1,-1)
        scanner.WriteLine()
        listing.WriteFooter()
        # parser.symboltable.Print()
        generator.PrintListing()
        break
    else:
        try:
            state = parser.ParseToken(token)
            parser.symboltable.HandleState(state,token)
            # parser.symboltable.Print()
            # symbolTable.Analyze(token);
        except SyntaxException as e:
            scanner.WriteLine()
            listing.ParsingError(e.__str__(),scanner.Line,scanner.Char)
        except MissingTokenException as e:
            listing.ParsingError(e.__str__(),-1,-1)
        except IdentifierExistsException as e:
            listing.SymbolTableError(e.__str__(),scanner.Line,scanner.Char)
        #TokenOut.write('%s\n' % token.__str__())
