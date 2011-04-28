Readme for PyMinJ v1.0 Compiler
===============================

Development
-----------
All of the included code was developed by Stephen Young (9736247) for the
purpose of Comp 442/6421, Winter 2011 (/4).

    @Author Stephen Young
    @Email  st_youn@encs.concordia.ca
    @UserID 9736247
    @Course Comp442/4

The ENCS originality form will be provided in class next week as an assurance
that this project has been uniquely developed by the above author, and that the
statements provided by this README document and the LanguageSpecification
document are truthful and legitimate.

Requirements:
-------------
This compiler was developed using Python 2.6.5 and should ideally be run using
this same version. It has been tested and produced no error in Python 2.4.3+,
however ideally will be run in a more recent environment.

The Pyminj compiler was developed on Windows 7 and tested on Windows, Cygwin and
Unix environments, to ensure cross-platform compatibility.

Usage:
------
Basic usage of the compiler at this stage is as follows:

    python compiler.py [path to file]

All output of the compiler is written to /output/. Each compilation will produce
two files, [filename].tokens and [filename].listing. These are respectively,
the listing of tokens found by the compiler during the scanning process, and the
listing of the file by the compiler during the scanning process.

Design Approach for the Scanner
-------------------------------
The Scanner was designed with the intention of optimal performance as well as
generic implementation. It is table driven and run using an underlying
deterministic finite automaton (DFA) designed to work using a .dfa configuration
file, which can be found in conf/pyminj.dfa. This is a custom designed
configuration file tailored together with the SimpleDFA class to work as a
robust, regular-expression driven DFA modelling structure, to suit the needs
of this language and compiler.

The design of the parser made cause for minor alterations to the scanner, in
particular the addition of a new class, ListingWriter, which handles the writing
of the listing. No changes have been made to the tokens or the handling of
tokens at this time.

In order to properly determine the end of function definitions, a new token type BLOCK_DELIMITER was added
representing an opening or closing curly bracket.

Test Cases
----------
In order to test the functionality of the scanner, several test cases have been
prepared, in the directory /test/. These can be run individually using:

    python compiler.py test/[filename]

Or in a batch using the special flag -t

    python compiler.py -t

All output will be directed to ./output/ as noted above

Design Approach for the Parser
------------------------------
The Parser was designed to adhere to the LL(1) approach to syntactical analysis
as well as work from a generic configuration file to ensure that additions to the
language can be added as members of the input grammar. It uses an implicit table-
driven approach that loads a resident grammar, and then parses tokens in the LL(1)
top-down fashion. All errors are reported within the output listing - which can
be found in /output/filename.listing.

The syntax grammar can be found in conf/syntax.ll1, as well as a brief overview of
how it is managed by the program. It is commented to make note of how the grammar
is being represented.

The parser has been adapted to call the symboltable at each pass in order to manage the insertion of identifiers
as well as to look up the value of identifiers to ensure that we can access them in the manner being attempted
by the developer.

A new layer was added to the parser, "MinjParser" extends the parser, and cleanly generates
a selective passing of tokens to the IntermediateGenerator, which in turn generates a 
'listing' containing logical blocks of code to be converted to three-code commands

Scope Rules
-----------
PyMinJ uses static scoping. Identifiers are unique to both a class itself and a
function within that class, and are searched for in reverse order of
generality For example:

[code lang='pyminj']
	class Test {
	
		int var1 = 1;
		
		int main(){
			char var1 = 'a';
			System.out(var1);			
		} // returns 'a'
		
		void print(){
			System.out(var1)
		} // returns 1;
	}
[/code]

In the above code snippet, a call to the main function returns a different value (and datatype) of var1
than a call to print, even though both call System.out(var1). PyMinJ will look for whichever value is
most specific to the given functional context, which will invariably be only either the <CLASS> context or
the context associated with the current <FUNCTION_NAME>. Note that no other code blocks (loops, conditions...)
will generate their own unique scope, only functions and classes. This eases simplicity and ensures that
the program understands very explicitly what it is able to access.

Structure of Symbol Table
-------------------------
The Symbol table to be used for PyMinJ is a collection of python dict objects. Since these are a natural and
well refined hash table architecture, they are ideal for this sort of data collection and persistence. When
interacting with the main symbol table wrapper, reference needs to be made as to the current subcontext. 
Since there are only two contextual levels, there is special dict in the symbol table data structure that
is representative of globally accessible values. The rest of the dicts are organized in a dict themselves,
indexed by context name. 

Properties stored by the Symbol Table
-------------------------------------
The symbol table stores basic core information about each identifier: the datatype of the identifier,
its name, the type (array,identifier[variable],function), as well as parameters for functions and 
size for arrays

Structure of the Symbol Table
-----------------------------
The symbol table is stored internally as a multidimensional python dictionary. This construct is
efficient because python's internals manage dictionaries as hash tables, making lookups available
in a constant amount of time O(1)

Efficiency of table management methods
--------------------------------------
Insertion onto the symbol table [SymbolTable.Insert(x)] is upper bounded by an O(n) efficiency, where n is the number of elements
in the table. Depending on scoping, and positioning of variables, the overall efficiency may be much better
than this. The use of python iterators as well eliminates a heavier lookup, by only retrieving the dict
keys necessary.
Searching the symbol table [SymbolTable.Search(x)] runs in O(1) time, maximally requiring only two 
hashtable lookups in order to find a symbol or determine that a symbol does not exist.
The rest of the handler functions provided in SymbolTable also run in a fixed time, and the overall runtime
for handlers minus insert is therefor equal to the average handler runtime multiplied by the number of tokens, 
since the handlers are called for each token.

Extra Semantics for PyMinJ
--------------------------

This implementation of MinJ relies on several extra semantic properties. 
	
	* The use of recursion is not permitted, and will result in an error at the intermediate code generation step
	* Variables are passed by reference in all instances
	* Internally, the return variable of a function is named 'return', to ensure that
	  we can manage references to it without danger of collision with user-defined
	  variables
	
Intermediate Code Generation
----------------------------

The intermediate code generated follows the following conventions:

	<method> <base> <param>

Where method is an intermediate code operation, param1 is what is referred in the source as
the 'base' identifier (the identifier to which a potential result will be pushed) and what
is referred to as the parameter, used differently by each operation

Generated intermediate code is inserted into /output/intermediate.tmp. Note this file will
only contain the intermediate code for the last compiled file, so the code for the files in
the auto-tester will only end up yielding the last file (class.min.mj).

Cached output for the auto-tester can be found in /output/cache/

Intermediate Code Instructions
------------------------------

Most of the instructions are fairly explanatory, and work as follows:

eg. add x 1, will add the value '1' to the value at address x
	add x x, will add the value at address x to the value at at address x
	
label <labelname> Indicates a logical label whose address needs to be stored in the next pass

btrue <var> <label> If the var resolves to true (1) branch to the address of <label>

bfalse <var> <label> Same as previous, but branches if the var is false (0)

return Returns the value of the runtime var 'return' to the return target, which will be defined
	   when the next pass is made that generates the frame header for the target code
	   
lt,gt,lte,gte,eq,neq These perform a check for whether or not <base> is <op> than <param>
					 so for lt x 10, if x is less than 10, x will be set to 1, otherwise
					 x is set to 0. In the generated code this is performed using temp
					 variables to ensure the stability of defined variables
					 
goto <label> Sends the execution cursor to the label

method <name> <start|end> Indicates the start and end of a method

pointer <var1> <var2> Creates a pointer to var2 at var1 (inserts address of var1 into var2)
advance <var1> <amount> Moves the pointer by <amount> addresses

Implementation of the Intermediate Code Generator
-------------------------------------------------

Two new modules were added:

	IntermediateGenerator
	This module generates logical blocks to be converted into intermediate code. It uses
	some basic parsing of the tokens to determine where these blocks start and end.
	
	ThreeCodeGenerator:
	This module uses a series of sequential and recursive calls to resolve tokens into a 
	series of commands
	
Intermediate code was designed to be simpler than Moon code, in order to make the translation process easier,
however I discovered that this raised some issues surrounding how to ensure that all the functionality is
represented optimally by both codes, and ultimately caused the translated code to be less efficient

Implementation of the Target Code Generator
-------------------------------------------

The target code generator, found in the module pyminj/MoonCompiler uses translation techniques to generate
Moon virtual machine compatible code from pyminj intermediate code.

Registers are allocated in a round-robin fashion, and the first four are stored as subroutine buffers (so
can be assumed by external libraries to be non-volatile - though the libraries need to declare what
buffers they will be using). The last register, r15 is used to store the return address of subroutines.

The target moon code is organized sequentially - frame headers are variadic in size, based on their sets
of parameters, and contain in order: all the parameters of the method, then all the variables defined for
this method.

Incomplete aspects of target code generation
--------------------------------------------

Due to personal time constraints, as well as overlooked bugs in the intermediate code
generation set, several aspects of target code generation are not, at this time, implemented:

	* The use of arrays is unpredictable, and will not yield proper results
	* Nesting of loops and conditional statements produces a missing label, which causes the branching to fail
	* Code following loops and conditions is occasionally not translated, due to the previous bug
	
	
Evaluation of compiler efficiency
---------------------------------

The efficiency of the compiler in its first phases is very good, but due to a lack of foresight and
some bad design decisions, the intermediate and target code generation phases do not produce optimal code.
The compiler is, despite these, relatively quick, moreso due to the small scale of the programs it
can produce, as well as the relative speed of the host system.

Compilation speed could be greatly increased with a second pass through the code to eliminate some of the 
read/write cycles, very often the code generates lines similar to:

lw	r8,t0(r0)
sw  c(r0),r8
lw	r9,c(r0)

Which could, depending on the case, be consolidated to potentially only one line. The overheads for this in
small programs is minimal, though it causes the virtual machine to do two slow memory accesses in a situation
where it could ideally only do one.

Error Handling
--------------

Errors are handled and reported solely within the code listing, and reported quietly to the user. The
compiler attempts to indicate where the error happened, but does nothing to attempt to fix the error once
it has occurred

Compiler Usage
--------------

The compiler can be run using the command:

python compiler.py -s FILE [-o OUTPUT] [-p]

the -o option allows the user to choose where the output will be sent
the -p option enables printing of the target code to stdout after compilation

Supplied with the compiler in /moon/ is the moon virtual machine (can be compiled with 'make')
and an integer printing library. To use this library, include it in the params for the moon
program when executing it, prior to the file compiled by PyMinJ

Future Improvements
-------------------

In the future, given time, I would like to complete the rest of the compilation process, as well as implementing
some basic optimization. I am also not happy with the design of my intermediate code, which became much more
difficult to work with than originally intended.

The biggest issue that arose in my design was the overall structure, which degraded as the compiler became
more complex. I would in the future, have liked to have spent the time mapping the modules and their
interaction, as well as a better idea of the structure of the intermediate code and its reflection as
moon code. While I attempted to adhere to many of the design principles discussed in lecture, it was difficult,
given a small amount of time, to maintain a full structure to the system.

Sample Code
-----------

In the /test/ directory are several samples of code. Their results can be found in the output directory.