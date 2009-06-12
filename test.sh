rm *.py
cp tests/test?*.py .
coverage -x testxstruct.py
coverage -x teststructures.py
coverage -x teststructureaccess.py
mkdir -p html
coverage -b -d html tp/netlib/xstruct.py tp/netlib/structures/*.py
rm *.py