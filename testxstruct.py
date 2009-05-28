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
		('c', ['a'], 'a'),
		('c', ['\x00'], '\x00'),
		
		('s', ['a'], 'a'),
		('s', ['\x00'], '\x00'),
		
		#8-bit integers
		('b', [127], '\x7f'),
		('b', [-128], '\x80'),
		
		('B', [0], '\x00'),
		('B', [255], '\xff'),
		
		#16-bit integers
		('h', [-32768], '\x80\x00'),
		('h', [32767], '\x7f\xff'),
		
		('H', [0], '\x00\x00'),
		('H', [65535], '\xff\xff'),
		
		('n', [-1], '\xff\xff'),
		('n', [0], '\x00\x00'),
		('n', [65534], '\xff\xfe'),
		
		#32-bit integers
		('i', [-2**31], '\x80\x00\x00\x00'),
		('i', [2**31-1], '\x7f\xff\xff\xff'),
		
		('I', [0], '\x00\x00\x00\x00'),
		('I', [2**32-1], '\xff\xff\xff\xff'),
		
		('j', [-1], '\xff\xff\xff\xff'),
		('j', [2**32-2], '\xff\xff\xff\xfe'),
		
		#64-bit integers
		('q', [-2**63], '\x80\x00\x00\x00\x00\x00\x00\x00'),
		('q', [2**63-1], '\x7f\xff\xff\xff\xff\xff\xff\xff'),
		
		('Q', [0], '\x00\x00\x00\x00\x00\x00\x00\x00'),
		('Q', [2**64-1], '\xff\xff\xff\xff\xff\xff\xff\xff'),
		
		('p', [-1], '\xff\xff\xff\xff\xff\xff\xff\xff'),
		('p', [2**64-2], '\xff\xff\xff\xff\xff\xff\xff\xfe'),
		
		#floats
		('f', [-2.**127], '\xff\x00\x00\x00'),
		('f', [-2.**-149], '\x80\x00\x00\x01'),
		('f', [2.**-149], '\x00\x00\x00\x01'),
		('f', [2.**127], '\x7f\x00\x00\x00'),
		
		('d', [-2.**1023], '\xff\xe0\x00\x00\x00\x00\x00\x00'),
		('d', [-2.**-1074], '\x80\x00\x00\x00\x00\x00\x00\x01'),
		('d', [2.**-1074], '\x00\x00\x00\x00\x00\x00\x00\x01'),
		('d', [2.**1023], '\x7f\xe0\x00\x00\x00\x00\x00\x00'),

		#timestamps
		('t', [datetime.fromtimestamp(0)], '\x00\x00\x00\x00'),
		('T', [datetime.fromtimestamp(0)], '\x00\x00\x00\x00\x00\x00\x00\x00'),
		]
	
	for structure, values, string in tests:
		assert pack(structure, *values) == string,\
			"Packing %s with %s should have given %s, but instead gave %s" % (values, structure, `string`, `pack(structure, *values)`)
		assert unpack(structure, string)[0] == tuple(values),\
			"Unpacking %s with %s should have given %s, but instead gave %s" % (`string`, structure, tuple(values), unpack(structure, *values)[0])
		assert unpack(structure, pack(structure, *values))[0] == tuple(values),\
			"Packing and unpacking %s with %s, but got %s" % (tuple(values), structure, unpack(structure, pack(structure, *values))[0])
		#we need to store this in a variable to use the unpack operator
		t = unpack(structure, string)[0]
		assert pack(structure, *t) == string,\
			"Unpacking and packing %s with %s, but got %s" % (string, structure, pack(structure, *t))

if __name__ == '__main__':
	test_pack_unpack()