Readme for PyMinJ v1.0 Compiler Final Project Submission
=======================================================

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

Usage of Registers
------------------

The registers in the Moon Machine are allocated as follows:

R(0) = 0
R(1) = STDOUT # This register is where data is written before being sent to stdout
R(2) =
R(3) =
R(4) = 
R(5) = 
R(5..16) = Volatile Memory