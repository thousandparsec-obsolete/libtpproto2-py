"""\
An advanced version of pack/unpack which works with extra TP strutures.

Everything is assumed to be network order, ie you don't need to
prepend every struct with !

Normal stuff from the struct module:

 c	Char
 b	Int8		(8 bit integer)
 B	UInt8		(8 bit unsigned integer)
 h	Int16		(16 bit integer)
 H	UInt16		(16 bit unsigned integer)
 i	Int32		(32 bit integer)
 I	UInt32		(32 bit unsigned integer)
 q	Int64		(64 bit integer)
 Q	UInt64		(64 bit unsigned integer)
 f	float		(32 bit floating point number)
 d	double		(64 bit floating point number)

Extra stuff defined by this module:

 S	String
 s	Char (identical to c)
 Y	Padded String	
 [	List Start		(unsigned int32 length)
 ]	List End	
 {	List Start		(unsigned int64 length)
 }	List End
 n	SInt16			(16 bit semi-signed integer)
 j	SInt32			(32 bit semi-signed integer)
 p	SInt64			(64 bit semi-signed integer)
 t	timestamp		(32 bit unsigned integer) 
 T	timestamp		(64 bit unsigned integer)
 
The structure of the data in the list is described by the data inside the
brackets.

Example:
	[L] would be a list of unsigned longs
	It is actually transmitted as <length><data><data><data>
	
Obviously you can't calculate size of an xstruct string. The unpack
function will return the unused data.

Limitations:
Even though t and T are unsigned integers, they are limited to a range from 0
to 2**31-1 seconds. This is because they are translated into datetime objects
from the datetime module, which uses a signed 32-bit timestamp.
"""

import pprint
import struct
import sys
import string
from types import *

# Squash errors about hex/oct
import warnings

_error = struct.error
_pack = struct.pack
_unpack = struct.unpack
_calcsize = struct.calcsize

semi = {'n':(16, 'H'), 'j':(32, 'I'), 'p':(64, 'Q')}
smallints = "njbBhHiI"
ints = {'b':8, 'B':8, 'h':16, 'H':16, 'i':32, 'I':32, 'q':64, 'Q':64}
times = {'T':'Q', 't':'I'}

def hexbyte(string):
	"""\
	Takes a string and prints out the bytes in hex.
	"""
#	return repr(string)
	s = ""
	for i in string:
		if (ord(i) >= ord('A') and ord(i) <= ord('z')) \
			or (ord(i) >= ord('0') and ord(i) <= ord('9')) \
			or (ord(i) == ord(" ")):
			s += "%s" % i
		else:
			s += "\\x%02x" % ord(i)

#		s += " "
	return s

def pack(sstruct, *aargs):
	"""\
	Takes a structure string and the arguments to pack in the format
	specified by string.
	"""
	struct  = sstruct
	args    = list(aargs)
	args_no = len(aargs)

	output = ""
	try:
		while len(struct) > 0:
			char = struct[0]
			struct = struct[1:]

			if char == ' ' or char == '!':
				continue
			elif char == '{':
				# Find the closing brace
				substruct, struct = string.split(struct, '}', maxsplit=1)
				output += pack_list('Q', substruct, args.pop(0))
			elif char == '[':
				# Find the closing brace
				substruct, struct = string.split(struct, ']', maxsplit=1)
				output += pack_list('I', substruct, args.pop(0))
			elif char in 'Tt':
				output += pack_time(args.pop(0), times[char])
			elif char == 'S':
				if not isinstance(args[0], (str, unicode, buffer)):
					raise TypeError("Argument should be an string (to pack to %s), not a %s" % (char, type(args[0])))
				output += pack_string(args.pop(0))
			elif char in 'cs':
				output += _pack("!c", args.pop(0))
			elif char in 'fd':
				output += _pack('!' + char, args.pop(0))
			elif char in string.digits:
				# Get all the numbers
				substruct = char
				while struct[0] in string.digits:
					substruct += struct[0]
					struct = struct[1:]
				# And the value the number applies to
				substruct += struct[0]
				struct = struct[1:]
				
				number = int(substruct[:-1])
				if substruct[-1] == 's':
					output += _pack("!"+substruct, args.pop(0))
				elif substruct[-1] == 'x':
					output += "\0" * number
				else:
					# Get the correct number of arguments
					new_args = []
					while len(new_args) < number:
						new_args.append(args.pop(0))
						
					output += apply(_pack, ["!"+substruct,] + new_args)
			else:
				if char in smallints and isinstance(args[0], long):
					args[0] = int(args[0])
				
				a = args.pop(0)

				# Check the type of the argument
				if not isinstance(a, (int, long)):
					raise TypeError("Argument should be an int or long (to pack to %s), not a %s" % (char, type(a)))

				if char in semi.keys():
					if a < -1:
						raise ValueError("Argument must be greater than or equal to -1 (to pack to %s) not %s" % (char, a))
					elif  a >= 2**semi[char][0]-1:
						raise ValueError("Argument must be less than %s (to pack to %s) not %s" % (2**semi[char][0]-1, char, a))
					elif a == -1:
						a = 2**semi[char][0]-1
					
					char = semi[char][1]
				elif char in ints and char.upper() == char:
					if a < 0:
						raise ValueError("Argument must be nonnegative (to pack to %s) not %s" % (char, a))
					elif a > 2**ints[char]-1:
						raise ValueError("Argument must be no greater than %s (to pack to %s) not %s" % (2**ints[char]-1, char, a))
				elif char in ints:
					if a < -2**(ints[char]-1):
						raise ValueError("Argument must be no less than %s (to pack to %s) not %s" % (-2**(ints[char]-1), char, a))
					elif a > 2**(ints[char]-1)-1:
						raise ValueError("Argument must be no greater than %s (to pack to %s) not %s" % (2**(ints[char]-1)-1, char, a))
				try:
					output += _pack("!"+char, a)
				except _error, e:
					# FIXME: Should do something better here!
					#print "Struct", char, "Args '%s'" % (a,)
					raise
	
	except TypeError, e:
		traceback = sys.exc_info()[2]
		while not traceback.tb_next is None:
			traceback = traceback.tb_next
		raise TypeError, "%i argument was the cause ('%s', %s)\n\t%s" % (len(aargs)-len(args)-1, sstruct, repr(aargs)[1:-1], str(e).replace('\n', '\n\t')), traceback
	except IndexError, e:
		traceback = sys.exc_info()[2]
		while not traceback.tb_next is None:
			traceback = traceback.tb_next
		raise TypeError, "Ran out of arguments, still had %s%s left of the structure" % (char, struct), traceback
	
	if len(args) > 0:
		raise TypeError("Had too many arguments! Still got the following remaining %r" % args)
	
	return output


def unpack(struct, s):
	"""\
	Takes a structure string and a data string.

	((values1,value2), remaining_data)
	
	"""
	output = []
	
	while len(struct) > 0:
		char = struct[0]
		struct = struct[1:]

		if char == ' ' or char == '!':
			continue
		elif char == '{':
			# Find the closing brace
			substruct, struct = string.split(struct, '}', maxsplit=1)
			data, s = unpack_list("Q", substruct, s)
			
			output.append(data)
		elif char == '[':
			# Find the closing brace
			substruct, struct = string.split(struct, ']', maxsplit=1)
			data, s = unpack_list("I", substruct, s)
			
			output.append(data)
		elif char in 'Tt':
			data, s = unpack_time(s, times[char])
			
			output.append(data)
		elif char == 'S':
			data, s = unpack_string(s)
			
			output.append(data)
		elif char in string.digits:
			# Get all the numbers
			substruct = char
			while struct[0] in string.digits:
				substruct += struct[0]
				struct = struct[1:]
			# And the value the number applies to
			substruct += struct[0]
			struct = struct[1:]
			
			size = _calcsize(substruct)
			size = _calcsize(substruct)
			if size > len(s):
				raise TypeError("Not enough data for %s, needed %s bytes got %r (%s bytes)" % (substruct[1:], size, s, len(s)))

			data = _unpack("!"+substruct, s[:size])
			s = s[size:]

			output += data
		else:
			if char in semi.keys():
				substruct = "!"+semi[char][1]
			else:
				substruct = "!"+char

			size = _calcsize(substruct)
			if size > len(s):
				raise TypeError("Not enough data for %s, needed %s bytes got %r (%s bytes)" % (substruct[1:], size, s, len(s)))

			try:
				data = _unpack(substruct, s[:size])
			except _error, e:
				print "Struct", substruct, "Args '%s'" % (s[:size],)
				raise
			s = s[size:]

			if char in semi.keys():
				if data[0] == 2**semi[char][0]-1:
					data = (-1,)
			output += data

	return tuple(output), s

def pack_list(length_struct, struct, args):
	"""\
	*Internal*

	Packs the id list so it can be send.
	"""
	# The length
	output = pack(length_struct, len(args))

	# The list
	for id in args:
		if type(id) == ListType or type(id) == TupleType:
			args = [struct] + list(id)
			output += apply(pack, args)
		else:
			output += pack(struct, id)
		
	return output

def unpack_list(length_struct, struct, s):
	"""\
	*Internal*

	Returns the first string from the input data and any remaining data.
	"""
	output, s = unpack(length_struct, s)
	length, = output

	list = []
	for i in range(0, length):
		try:
			output, s = unpack(struct, s)
		except TypeError, e:
			raise TypeError("Problem unpacking list item (index %s): %s" % (i, e))

		if len(output) == 1:
			list.append(output[0])
		else:
			list.append(output)

	return list, s

def pack_string(s):
	"""\
	*Internal*

	Prepares a string to be send out on a wire.
	
	It appends the string length to the beginning and adds a 
	null terminator.
	"""
	s = unicode(s).encode('utf-8')
	
	temp = s
	return pack("!I", len(temp)) + temp


import encodings
import encodings.utf_8
def unpack_string(s):
	"""\
	*Internal*

	Returns the first string from the input data and any remaining data.
	"""
	# Totally empty string
	if len(s) == 0:
		return "", s
	
	# Remove the length
	try:
		(l, ), s = unpack("I", s)
	except TypeError, e:
		raise TypeError("Problem unpacking length of string: %s" % e)

	if l > 0:
		# Get the string, (we don't need the null terminator so nuke it)
		if len(s) < l:
			raise TypeError("Not enough data for string, length said %s bytes got %r (%s bytes)" % (l, s, len(s)))

		output = s[:l]
		s = s[l:]
		
		# Remove any extra null terminators.
		if output[-1] == '\0':
			output = output[:-1]

		# Make sure the string is a valid utf-8 string
		# If the sender is well behaved this does nothing...
		output = encodings.utf_8.decode(output, errors='ignore')[0]

		return output, s
	else:
		return "", s


import time
from datetime import datetime

def unpack_time(s, type='I'):
	"""\
	*Internal*

	Returns the datetime object and any remaining data.
	"""
	try:
		(l,), s = unpack("!"+type, s)
	except TypeError, e:
		raise TypeError("Problem unpacking time: %s" % e)

	if l < 0:
		return None
	return datetime.fromtimestamp(l), s

def pack_time(t, type='I'):
	"""\
	*Internal*

	Returns the datetime object and any remaining data.
	"""
	if t is None:
		t = -1
	elif isinstance(t, datetime):
		t = long(time.mktime(t.timetuple()))
	elif isinstance(t, float):
		# FIXME: This should be a depreciated warning...
		print "Warning! pack_time called with float"
		t = long(t)
	elif not isinstance(t, (int, long)):
		raise TypeError("Not a valid type for pack_time")
	s = pack("!"+type, t)
	return s

