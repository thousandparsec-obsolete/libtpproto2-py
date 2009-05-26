from tp.netlib.xstruct import *

def test_pack_upnack():
	tests = [
		('c', ('a',))
		]
	for i, j in tests:
		assert unpack(i, pack(i, *j))[0] == j

if __name__ == '__main__':
	test_pack_upnack()