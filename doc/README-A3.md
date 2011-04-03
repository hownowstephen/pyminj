Readme for PyMinJ v1.0 Compiler Milestone 3
===========================================

Development
-----------
All of the included code was developed by Stephen Young (9736247) for the
purpose of Comp 442/6421, Winter 2011 (/4).

    @Author Stephen Young
    @Email  st_youn@encs.concordia.ca
    @UserID 9736247
    @Course Comp442/4

Requirements for this application can be found in README-A1.txt, the readme file
associated with the first milestone of this compiler

Please read notes on test cases in README-A2.txt. Output of the compiler at present is a
full final listing of the symbol table. Errors can be viewed in the listing, but are currently
not reported to STDOUT. 

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

Changes to Scanner (A1)
-----------------------
In order to properly determine the end of function definitions, a new token type BLOCK_DELIMITER was added
representing an opening or closing curly bracket.

Changes to Parser (A2)
----------------------
The parser has been adapted to call the symboltable at each pass in order to manage the insertion of identifiers
as well as to look up the value of identifiers to ensure that we can access them in the manner being attempted
by the developer.