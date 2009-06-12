#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

import unittest
from datetime import datetime

from tp.netlib.structures import *
from tp.netlib.xstruct import pack, unpack

def extend(cls):
	class extension(cls):
		pass
	return extension

class TestStructures(unittest.TestCase):
	def test_character(self):
		#good values
		CharacterStructure("character")
		strings = ['', 'a' '123']
		for string in strings:
			length = len(string)
			structure = CharacterStructure("character", size=length)
			self.assertTrue(structure.check(string))
			self.assertEqual(structure.length(string), length)
			self.assertEqual(pack(structure.xstruct, string), string,
				"CharacterStructure's xstruct is talking crazy for %r" % (string,))
		
		#bad values
		structure = CharacterStructure("character", size=1)
		self.assertRaises(ValueError, structure.check, 0)
		self.assertRaises(ValueError, structure.check, 0.)
		self.assertRaises(ValueError, structure.check, None)
		self.assertRaises(ValueError, structure.check, '')
		self.assertRaises(ValueError, structure.check, '12')
	
	def test_datetime(self):
		#good values
		small = DateTimeStructure("time", size=32)
		large = DateTimeStructure("time")
		large = DateTimeStructure("time", size=64)
		times = [0, 5, 2**31-1]
		for time in times:
			time = datetime.fromtimestamp(time)
			self.assertEqual(small.length(time), 4)
			self.assertEqual(large.length(time), 8)
			self.assertTrue(small.check(time))
			self.assertTrue(large.check(time))
		self.assertEqual(small.xstruct, "t")
		self.assertEqual(large.xstruct, "T")
		
		#bad values
		self.assertRaises(ValueError, lambda: DateTimeStructure("smallTime", size=16))
		
		
		#the following tests can't be run because fromtimestamp finds the overflows
		#before they can reach the structure for testing
		#self.assertRaises(ValueError, small.check, datetime.fromtimestamp(-1))
		#self.assertRaises(ValueError, small.check, datetime.fromtimestamp(2**31))
		
		self.assertRaises(ValueError, small.check, 1)
		self.assertRaises(ValueError, small.check, ())
		self.assertRaises(ValueError, small.check, [])
		self.assertRaises(ValueError, small.check, {})
		self.assertRaises(ValueError, small.check, None)
	
	def test_enumeration(self):
		structure = EnumerationStructure("enumeration", values=
			{'a':0, 'b':1, 'c':2})
		
		#good values
		self.assertTrue(structure.check(0))
		self.assertTrue(structure.check(1L))
		self.assertTrue(structure.check('b'))
		self.assertTrue(structure.check(u'c'))
		
		#bad values
		self.assertRaises(ValueError, structure.check, -1)
        	self.assertRaises(ValueError, structure.check, 3)
		self.assertRaises(ValueError, structure.check, 'q')
		self.assertRaises(TypeError, structure.check, None)
		self.assertRaises(TypeError, structure.check, 0.)
		self.assertRaises(TypeError, structure.check, [])
		self.assertRaises(TypeError, structure.check, ())
		self.assertRaises(TypeError, structure.check, {})
		self.assertRaises(ValueError, lambda: EnumerationStructure("enumeration", values={'a':'b'}))
		self.assertRaises(TypeError, lambda: EnumerationStructure("enumeration", values={1:0}))
	
	def test_group(self):
		structure = GroupStructure("group",  structures=[
			IntegerStructure("A"), StringStructure("B")])
		
		#good values
		self.assertTrue(structure.check([4, 'ABC']))
		self.assertTrue(structure.check((4, 'ABC')))
		self.assertEquals(structure.length([4, 'ABC']), 11)
		self.assertEquals(structure.xstruct, "iS")
		self.assertEquals(GroupStructure("group").xstruct, "")
		
		#bad values
		self.assertRaises(ValueError, structure.check, [])
		self.assertRaises(ValueError, structure.check, None)
		self.assertRaises(ValueError, structure.check, [3,4])
		self.assertRaises(ValueError, structure.check, [3, "ABC", 4])
		self.assertRaises(ValueError, structure.check, extend(list)())
		self.assertRaises(ValueError, structure.check, extend(tuple)())
		self.assertRaises(ValueError, lambda: GroupStructure("group", structures=1))
		self.assertRaises(ValueError, lambda: GroupStructure("group", structures=1.))
		self.assertRaises(ValueError, lambda: GroupStructure("group", structures=None))
		self.assertRaises(ValueError, lambda: GroupStructure("group", structures={}))
		self.assertRaises(ValueError, lambda: GroupStructure("group", structures=[1]))
	
	
	
	def test_integer(self):
		for size in (8, 16, 32, 64):
			for sign in ('signed', 'unsigned', 'semisigned'):
				if size == 8 and sign == 'semisigned':
					#only combination that dosent exist
					continue
				if sign == 'signed':
					min = -2**(size-1)
					max = 2**(size-1)-1
				if sign == 'unsigned':
					min = 0
					max = 2**(size)-1
				if sign == 'semisigned':
					min = -1
					max = 2**(size)-2
				
				#good values
				structure = IntegerStructure('int', size=size, type=sign)
				
				self.assertEqual(structure.length(min), size/8)
				self.assertTrue(structure.check(min))
				self.assertTrue(structure.check(max))
				
				format = structure.xstruct
				self.assertEqual(unpack(format, pack(format, min))[0][0], min)
				self.assertEqual(unpack(format, pack(format, max))[0][0], max)
				
				#bad values
				self.assertRaises(ValueError, structure.check, min-1)
				self.assertRaises(ValueError, structure.check, max+1)
				self.assertRaises(ValueError, structure.check, 0.)
				self.assertRaises(ValueError, structure.check, '')
				self.assertRaises(ValueError, structure.check, None)
		
		self.assertRaises(ValueError, lambda: IntegerStructure('int', size=7))
		self.assertRaises(ValueError, lambda: IntegerStructure('int', type='supersigned'))
	
	def test_list(self):
		structure = ListStructure("group",  structures=[
			IntegerStructure("A"), StringStructure("B")])
		structure2 = ListStructure("group",  structures=[IntegerStructure("A")])
		
		#good values
		self.assertTrue(structure.check([[4, 'ABC']]))
		self.assertTrue(structure.check([]))
		self.assertTrue(structure.check([[4, 'ABC'], [4, '123']]))
		self.assertTrue(structure.check(extend(list)()))
		self.assertTrue(structure2.check([]))
		
		self.assertEquals(structure.length([[4, 'ABC']]), 15)
		self.assertEquals(structure.length([]), 4)
		self.assertEquals(structure.length(extend(list)()), 4)
		self.assertEquals(structure2.length([]), 4)
		self.assertEquals(structure2.length([1]), 8)
		
		self.assertEquals(structure.xstruct, '[iS]')
		
		#bad values
		self.assertRaises(ValueError, structure.check, None)
		self.assertRaises(ValueError, structure.check, 4)
		self.assertRaises(ValueError, structure.check, [3,4])
		self.assertRaises(ValueError, structure.check, [3])
		self.assertRaises(ValueError, structure.check, [[3]])
		self.assertRaises(ValueError, structure.check, [[4, 'ABC'], [4, 23]])
	
	def test_string(self):
		strings = ['A', '\x00\x01', u'Ж', u'中', u'\U00010346']
		structure = StringStructure("string")
		self.assertEqual(structure.xstruct, 'S',
			"StringStructure's xstruct is %r instead of 'S'" % (structure.xstruct,))
		
		#good values
		for string in strings:
			try:
				structure.check(string)
			except:
				self.fail("StringStructure said %r is not valid" % (string,))
			self.assertEqual(structure.length(string), len(pack(structure.xstruct, string)))
		
		#bad values
		self.assertRaises(ValueError, structure.check, 0)
		self.assertRaises(ValueError, structure.check, 0.)
		self.assertRaises(ValueError, structure.check, None)
	
	def test_structure(self):
		class test(Structure):
			pass
		self.assertRaises(NotImplementedError, Structure, "test")
		self.assertRaises(ValueError, Structure)
		t = test("test")
		self.assertRaises(NotImplementedError, t.check, None)
		self.assertRaises(NotImplementedError, t.length, None)
		self.assertRaises(NotImplementedError, lambda: t.xstruct)
		self.assertTrue(str(t).startswith("<test "))
		self.assertTrue(str(t).endswith(" test>"))
		

if __name__ == '__main__':
	unittest.main()