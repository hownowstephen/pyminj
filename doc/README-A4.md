Readme for PyMinJ v1.0 Compiler Milestone 4
===========================================

Development
-----------
All of the included code was developed by Stephen Young (9736247) for the
purpose of Comp 442/6421, Winter 2011 (/4).

    @Author Stephen Young
    @Email  st_youn@encs.concordia.ca
    @UserID 9736247
    @Course Comp442/4

Requirements for this application can be found in README-A1.md, the readme file
associated with the first milestone of this compiler

Please read notes on test cases in README-A2.md. Output of the compiler at present is a
full final listing of the symbol table. Errors can be viewed in the listing, but are currently
not reported to STDOUT. 

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

Intermediate Code Instructions
------------------------------

Most of the instructions are fairly explanatory, and work as follows:

eg. add x 1, will add the value '1' to the value at address x
	add x x, will add the value at address x to the value at at address x
	
label <labelname> Indicates a logical label whose address needs to be stored in the next pass

branch_true <var> <label> If the var resolves to true (1) branch to the address of <label>

branch_false <var> <label> Same as previous, but branches if the var is false (0)

return Returns the value of the runtime var 'return' to the return target, which will be defined
	   when the next pass is made that generates the frame header for the target code
	   
lt,gt,lte,gte,eq,neq These perform a check for whether or not <base> is <op> than <param>
					 so for lt x 10, if x is less than 10, x will be set to 1, otherwise
					 x is set to 0. In the generated code this is performed using temp
					 variables to ensure the stability of defined variables
					 
tmp# is a reference to a temporary variable, which is allocated round-robin. 12 slots are
	 currently allowed for these, pending a final decision in the target code generation
	 phase
	 
goto <label> Sends the execution cursor to the label

method <name> <start|end> Indicates the start and end of a method

pointer <var1> <var2> Creates a pointer to var2 at var1 (inserts address of var1 into var2)
advance <var1> <amount> Moves the pointer by <amount> addresses
Implementation
--------------

Two new modules were added:

	IntermediateGenerator
	This module generates logical blocks to be converted into intermediate code. It uses
	some basic parsing of the tokens to determine where these blocks start and end.
	
	ThreeCodeGenerator:
	This module uses a series of sequential and recursive calls to resolve tokens into a 
	series of commands

Changes to Scanner (A1)
-----------------------

No changes were made to the scanner

Changes to Parser (A2)
----------------------

A new layer was added to the parser, "MinjParser" extends the parser, and cleanly generates
a selective passing of tokens to the IntermediateGenerator, which in turn generates a 
'listing' containing logical blocks of code to be converted to three-code commands

Changes to Symbol Table (A3)
----------------------------

No changes were made to the symbol table