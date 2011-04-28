#!/usr/bin/python
import sys
import os.path as filepath
import os
from pyminj import *
from optparse import OptionParser

Version = '1.0.0'
Author = 'Stephen Young (st_youn@encs.concordia.ca)'

# Options

optparser = OptionParser()
optparser.add_option("-s", "--src", dest="srcfile",
                  help="Defines the minJ file to be compiled", metavar="FILE")
optparser.add_option("-o", "--out", dest="targetfile",
                  help="Defines the mooncode file to be generated", metavar="FILE")
optparser.add_option("-p", "--print", dest="printsrc",action="store_true",
                  help="Defines whether or not the moon code is printed to stdout")

(options, args) = optparser.parse_args()

fname = options.srcfile
if not fname:
    print "No source file specified!"
    sys.exit(1)
    
if not options.targetfile:
    options.targetfile = "%s.m" % filepath.basename(options.srcfile)
    print "Warning: No target file selected, defaulting to %s" % options.targetfile

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


err = False

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
        #parser.symboltable.Print()
        try:
            parser.CheckStack()
        except MissingTokenException as e:
            listing.ParsingError(e.__str__(),-1,-1)
            err = True 
        
        scanner.WriteLine()
        listing.WriteFooter()
        # parser.symboltable.Print()
        generator.PrintListing()
        
        if err: 
            print "An error occurred in compilation, please consult the listing"
            sys.exit()   
        
        moon_compiler = MoonCompiler(options.targetfile,parser.symboltable.GetTable())
        moon_compiler.Compile()
        moon_compiler.WriteMFile()
        
        if options.printsrc:
            os.system("cat %s" % options.targetfile)
        
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
            err = True
        except MissingTokenException as e:
            listing.ParsingError(e.__str__(),-1,-1)
            err = True
        except IdentifierExistsException as e:
            listing.SymbolTableError(e.__str__(),scanner.Line,scanner.Char)
            err = True
        except:
            err = True
        #TokenOut.write('%s\n' % token.__str__())
