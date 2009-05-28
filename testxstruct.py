from datetime import datetime

from tp.netlib.xstruct import *

def now():
	"""\
	This function is needed because xstruct's representation is only accurate to the second
	"""
	time = datetime.now()
	return datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)

def test_pack_unpack():
	#these are all tuples of (structure, values, string representation)
	tests = [
		#characters
		('c', ('a',), 'a'), ('cc', ('A', 'd'), 'Ad'), ('c', ('\x00',), '\x00'),
		('s', ('a',), 'a'), ('ss', ('A', 'd'), 'Ad'), ('s', ('\x00',), '\x00'),
		#8-bit integers
		('b', (1,), '\x01'), ('bbbb', (0,-1,127,-128), '\x00\xff\x7f\x80'),
		('B', (1,), '\x01'), ('BBBB', (0,1,128,255), '\x00\x01\x80\xff'),
		#16-bit integers
		('h', (1,), '\x00\x01'), ('hhhh', (0,-1,32767,-32768), '\x00\x00\xff\xff\x7f\xff\x80\x00'),
		('H', (1,), '\x00\x01'), ('HHHH', (0,1,32768,65535), '\x00\x00\x00\x01\x80\x00\xff\xff'),
		('n', (1,), '\x00\x01'), ('nnnn', (0,-1,32768,65534), '\x00\x00\xff\xff\x80\x00\xff\xfe'),
		#32-bit integers
		('i', (1,), '\x00\x00\x00\x01'), ('iiii', (0,-1,2**31-1,-(2**31)), '\x00\x00\x00\x00\xff\xff\xff\xff\x7f\xff\xff\xff\x80\x00\x00\x00'),
		('I', (1,), '\x00\x00\x00\x01'), ('IIII', (0,1,2**16-1,2**32-1), '\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xff\xff\xff\xff\xff\xff'),
		('j', (1,), '\x00\x00\x00\x01'), ('jjjj', (0,-1,2**16-1,2**32-2), '\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\xff\xff\xff\xff\xff\xfe'),
		#64-bit integers
		('q', (1,), '\x00\x00\x00\x00\x00\x00\x00\x01'),
		('qqqq', (0,-1,2**63-1,-(2**63)), '\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\x80\x00\x00\x00\x00\x00\x00\x00'),
		('Q', (1,), '\x00\x00\x00\x00\x00\x00\x00\x01'),
		('QQQQ', (0,1,2**16-1,2**64-1), '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
		('p', (1,), '\x00\x00\x00\x00\x00\x00\x00\x01'),
		('pppp', (0,-1,2**16-1,2**64-2), '\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe'),
		#floats
		('f', (1.,), '?\x80\x00\x00'), ('ffff', (-2.**127, -2.**-149, 2.**-149, 2.**127), '\xff\x00\x00\x00\x80\x00\x00\x01\x00\x00\x00\x01\x7f\x00\x00\x00'),
		('d', (1.,), '?\xf0\x00\x00\x00\x00\x00\x00'),
		('dddd', (-2.**1023, -2.**-1074, 2.**-1074, 2.**1023), '\xff\xe0\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x7f\xe0\x00\x00\x00\x00\x00\x00'),
		#timestamps
		('t', (datetime.fromtimestamp(0),), '\x00\x00\x00\x00'),
		('T', (datetime.fromtimestamp(0),), '\x00\x00\x00\x00\x00\x00\x00\x00'),
		]
	
	for i, j, k in tests:
		assert pack(i, *j) == k, "Packing %s with %s should have given %s, but instead gave %s" % (j, i, k, pack(i, *j))
		assert unpack(i, k)[0] == j, "Unpacking %s with %s should have given %s, but instead gave %s" % (k, i, j, unpack(i, *j)[0])
		assert unpack(i, pack(i, *j))[0] == j, "Packing and unpacking %s with %s, but got %s" % (j, i, unpack(i, pack(i, *j))[0])
		#we need to store this in a variable to use the unpack operator
		t = unpack(i, k)[0]
		assert pack(i, *t) == k, "Unpacking and packing %s with %s, but got %s" % (k, i, pack(i, *t))

if __name__ == '__main__':
	test_pack_unpack()