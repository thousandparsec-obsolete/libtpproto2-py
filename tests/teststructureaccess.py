#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from tp.netlib.structures import *
from tp.netlib.xstruct import unpack


class TestStructureAccess(unittest.TestCase):
	def test_access(self):
		class test(object):
			i = IntegerStructure("i")
			s = StringStructure("s")
			g = GroupStructure("g", structures=[StringStructure("s"), GroupStructure("g", structures=[StringStructure("s")])])
		
		obj = test()
		
		self.assertRaises(AttributeError, lambda: obj.i)
		obj.i = 3
		self.assertEquals(obj.i, 3)
		self.assertFalse(obj.i != 3)
		
		value = unpack(test.i.xstruct, test.i.pack(obj))[0][0]
		self.assertEqual(obj.i, value)
		test.i.unpack(obj, test.i.pack(obj))
		self.assertEqual(obj.i, value)
		
		del obj.i
		self.assertRaises(AttributeError, lambda: obj.i)
		
		obj.s = "test"
		self.assertEquals(obj.s, "test")
		
		obj.g = ["foo", ["bar"]]
		self.assertEquals(obj.g.s, "foo")
		self.assertEquals(obj.g.g.s, "bar")
		self.assertEquals(obj.g, ["foo", ["bar"]])
		self.assertTrue(obj.g != [])
		
		test.g.unpack(obj, test.g.pack(obj))
		self.assertEqual(obj.g, ["foo", ["bar"]])
		
		obj.g[0] = "oof"
		self.assertEquals(obj.g[0], "oof")
		del obj.g[0]
		self.assertRaises(AttributeError, lambda: obj.g[0])
		self.assertRaises(AttributeError, lambda: obj.g.s)
		self.assertRaises(AttributeError, lambda: obj.g.x)
		obj.g.s = "foo"
		self.assertEquals(obj.g.s, "foo")
		try:
			obj.g.x = 0
			self.fail("Assigning a non-existent member of a GroupStructure didn't fail.")
		except AttributeError, e:
			pass
		
		del obj.g.s
		try:
			del obj.g.x
			self.fail("Deleting a non-existent member of a GroupStructure didn't fail.")
		except AttributeError, e:
			pass
		
		del obj.g
	
	def test_list_access(self):
		class test(object):
			l = ListStructure("l", structures=[StringStructure("s"), CharacterStructure("c")])
			l2 = ListStructure("l2", structures=[StringStructure("s")])
			l3 = ListStructure("l3", structures=[IntegerStructure("i")])
		
		obj = test()


		obj.l = []
		self.assertEquals(len(obj.l), 0)
		self.assertEquals(obj.l, [])


		obj.l = [['abc', '\x00']]
		self.assertEquals(obj.l[0], ['abc', '\x00'])
		self.assertEquals(obj.l, [['abc', '\x00']])
		
		self.assertNotEquals(obj.l, [[]])
		self.assertNotEquals(obj.l, [])
		self.assertNotEquals(obj.l, [[], []])
		#this test differs from the above:
		#assertNotEquals(a,b) asserts not a == b, this asserts a != b
		#these are different statements
		self.assertTrue(obj.l != [])
		
		
		obj.l[0] = ['1', '2']
		obj.l.insert(1, ['3', '4'])
		self.assertEquals(obj.l.pop(1), ['3', '4'])
		del obj.l[0]
		self.assertEqual(len(obj.l), 0)
		obj.l[0:] = [['a', 'b'], ['c', 'd']]
		self.assertEqual(obj.l, [['a', 'b'], ['c', 'd']])
		obj.l.append(['e', 'f'])
		self.assertEqual(obj.l, [['a', 'b'], ['c', 'd'], ['e', 'f']])
		del obj.l
		
		obj.l2 = ["ab", "cd", "ef"]
		self.assertEquals(obj.l2, ["ab", "cd", "ef"])
		self.assertEquals(len(obj.l2), 3)
		obj.l2[1] = "CD"
		self.assertEquals(obj.l2, ["ab", "CD", "ef"])
		obj.l2[1:-1] = ["cd"]
		self.assertEquals(obj.l2, ["ab", "cd", "ef"])
		del obj.l2[1]
		self.assertEquals(obj.l2, ["ab", "ef"])
		self.assertEquals(len(obj.l2), 2)
		
		for i, j in zip(obj.l2, ["ab", "ef"]):
			self.assertEquals(i, j)
		self.assertEquals(obj.l2 + ["gh"], ["ab", "ef", "gh"])
		self.assertEquals(obj.l2 * 2, ["ab", "ef", "ab", "ef"])
		self.assertEquals(2 * obj.l2, ["ab", "ef", "ab", "ef"])
		self.assertTrue("ef" in obj.l2)
		self.assertFalse("ef" not in obj.l2)
		self.assertFalse("CD" in obj.l2)
		self.assertTrue("CD" not in obj.l2)
		obj.l2.append("gh")
		self.assertEqual(obj.l2, ["ab", "ef", "gh"])
		self.assertEqual(list(reversed(obj.l2)), ["gh", "ef", "ab"])
		obj.l2.reverse()
		self.assertEqual(obj.l2, ["gh", "ef", "ab"])
		obj.l2.sort()
		self.assertEqual(obj.l2, ["ab", "ef", "gh"])
		
		obj.l3 = [2]
		self.assertTrue(obj.l3 < [3])
		self.assertTrue(obj.l3 <= [3])
		self.assertTrue(obj.l3 <= [2])
		self.assertTrue(obj.l3 > [1])
		self.assertTrue(obj.l3 >= [1])
		self.assertTrue(obj.l3 >= [2])
		
		
		obj.l3 = range(10)
		self.assertEqual(obj.l3, [0,1,2,3,4,5,6,7,8,9])
		self.assertEqual(obj.l3[1:8], [1,2,3,4,5,6,7])
		self.assertEqual(obj.l3[1:8:2], [1,3,5,7])
		self.assertEqual(obj.l3.count(2), 1)
		self.assertEqual(obj.l3.pop(0), 0)
		obj.l3.insert(0,0)
		self.assertEqual(obj.l3, [0,1,2,3,4,5,6,7,8,9])
		self.assertEqual(obj.l3.index(1), 1)
		obj.l3.extend([10,11,12,13])
		self.assertEqual(obj.l3, [0,1,2,3,4,5,6,7,8,9,10,11,12,13])
		obj.l3.reverse()
		self.assertEqual(obj.l3, [13,12,11,10,9,8,7,6,5,4,3,2,1,0])
		obj.l3.remove(5)
		self.assertEqual(obj.l3, [13,12,11,10,9,8,7,6,4,3,2,1,0])
		obj.l3[0:13:2] = [13,11,9,7,4,2,0]
		self.assertEqual(obj.l3, [13,12,11,10,9,8,7,6,4,3,2,1,0])
		
		#Need a function to test illegal assignment with List
		def assign(object):
			object[1:9:2] = [2]
		
		self.assertRaises(ValueError, assign, obj.l3)
		
		value = unpack(test.l3.xstruct, test.l3.pack(obj))[0][0]
		self.assertEqual(obj.l3, value)
		test.l3.unpack(obj, test.l3.pack(obj))
		self.assertEqual(obj.l3, value)

if __name__ == '__main__':
	unittest.main()
