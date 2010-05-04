#!/bin/sh

#Because messing with paths tends to confuse coverage tests, copy the tests here
#so that the library is on the path
cp tests/test?*.py .

#run the tests
coverage -e
coverage -x testxstruct.py
coverage -x teststructures.py
coverage -x teststructureaccess.py
coverage -x testparser.py
coverage -x testpacking.py

#generate the html report
mkdir -p html
coverage -b -d html tp/netlib/xstruct.py tp/netlib/structures/*.py tp/netlib/parser.py

#get rid of the tests
rm *.py
