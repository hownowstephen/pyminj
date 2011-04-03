#!/bin/sh
echo "\tRunning tests..."

echo "\tRunning error-free file"
python compiler.py test/class.noerr.mj > /dev/null

echo "\tRunning cascading-error file"
python compiler.py test/class.multierr.mj > /dev/null

echo "\tRunning unterminated-error file"
python compiler.py test/class.unterminated.mj > /dev/null

echo "\tRunning file displaying all errors"
python compiler.py test/class.allerrors.mj > /dev/null

echo "\tRunning minimalistic file"
python compiler.py test/class.min.mj > /dev/null

echo "\tRunning symbol table error file"
python compiler.py test/class.symbolerr.mj > /dev/null

echo "\tTest suite complete"
