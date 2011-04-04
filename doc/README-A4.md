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
	
Intermediate Code Generation
----------------------------

The intermediate code generated follows the following conventions:

	<scope> <method> <param1> <param2>
	
In this case, scope is represented by a single enumerated value which in turn corresponds to the
scope of the current method. By default, the program has a scope of 0 and the main method has a scope 
of 1, and all others have a scope that is assigned based on the order in which they are defined (so the 
first user function will be scope 2 etc). The values of variables are searched first in the symbol table 
for the current defined scope and then within the global scope 0.
	

Implementation
--------------


Changes to Scanner (A1)
-----------------------

Changes to Parser (A2)
----------------------

Changes to Symbol Table (A3)
----------------------------