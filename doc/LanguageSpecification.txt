##########################################
# Language Specification for PyMinJ v1.0 #
##########################################

Overview
--------

PyMinJ is a pure-python implementation of a MinJ compiler based on the language
standards provided by Prof. J. Opatrny for Comp 442/6421, Winter 2011 (/4)

Language Principles
-------------------
PyMinJ is implemented as a free-format language, in which all tokens are
assumed to be the longest substring, and are terminated by either the starting
character of another token or whitespace.

Comments
--------
Comments in PyMinJ are slightly different from the initial specification and are
defined by the regular expression:

    comment = #c*(\n|EOF)

So a comment begins with a hash symbol and is terminated by either a newline
or the end of file. The // convention was replaced by # to approach the language
by following what can be considered more of a Unix-compatible implementation,
as well as to provide simplicity in scanning and tokenizing the code

Whitespace
----------
PyMinJ recognizes whitespace as being any of ' ', '\n', '\t', or the Python
special type None (which corresponds to the EOF marker while reading through
a file). Whitespace is used, as noted above, to delimit tokens, and as such can
be used at any place within the code. However, usage of whitespace may change
the logical understanding of tokens, because it is one of the deciding factors
the compiler relies on to understand the difference between two adjacent tokens.

Identifiers
-----------
Are to be limited to 32 characters, of which all 32 characters are used as
a uniquely distinguishable key. This restriction will ensure that all
identifiers are unique and help avoid confusion.

Numerical Constants
-------------------
Restricted to signed integers between -2147483648 and 2147483648 to cater
to 32-bit architectures

Case-sensitivity
----------------
PyMinJ follows the Unix standard of case sensitivity, in order to maximize the
effectiveness of the language and the availability of identifiers. Lower case
characters are therefor not equivalent to upper case characters in any case.
Reserved keywords are only reserved for the case represented below, all other
case combinations may form user-defined identifiers.

Tokens
------
The PyMinJ compiler recognizes the following token types in its scanning process.
Malformed tokens will result in an InvalidTokenException, as noted in the
Errors portion of this document

          IDENT:    [a-zA-Z_$][a-zA-Z0-9_$]*
        NUMERIC:    -?\d+
CHARACTER_CONST:    'c'                        # where c is any character
       OPERATOR:    (+|*|/|%)
       OP_MINUS:    -                          # operator and negative sign
        COMPARE:    (<|>|!)
       COMPARE2:    (<=|>=|!=|==)
         ASSIGN:    =
      DELIMITER:    (\(|\)|\}|\{|\[|\]|\.|,|;) # Brackets, dot, comma, semicolon
      LOGIC_AND:    &&
       LOGIC_OR:    ||


Errors
------
InvalidTokenException (Scanner): Thrown when a malformed or unknown token is
                                 encountered by the scanner
