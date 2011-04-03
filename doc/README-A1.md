Readme for PyMinJ v1.0 Compiler Milestone 1
===========================================

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

Design Approach
---------------
The Scanner was designed with the intention of optimal performance as well as
generic implementation. It is table driven and run using an underlying
deterministic finite automaton (DFA) designed to work using a .dfa configuration
file, which can be found in conf/pyminj.dfa. This is a custom designed
configuration file tailored together with the SimpleDFA class to work as a
robust, regular-expression driven DFA modelling structure, to suit the needs
of this language and compiler.

Test Cases
----------
In order to test the functionality of the scanner, several test cases have been
prepared, in the directory /test/. These can be run individually using:

    python compiler.py test/[filename]

Or in a batch using the special flag -t

    python compiler.py -t

All output will be directed to ./output/ as noted above