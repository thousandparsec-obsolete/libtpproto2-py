import sys
sys.path.insert(0, '..')

import unittest

from tp.netlib.structures import *


class TestStructureAccess(unittest.TestCase):
	def test_access(self):
		class test(object):
			i = IntegerStructure("i")
			s = StringStructure("s")
			g = GroupStructure("g", structures=[StringStructure("s"), GroupStructure("g", structures=[StringStructure("s")])])
			l = ListStructure("l", structures=[StringStructure("s"), CharacterStructure("c")])
			l2 = ListStructure("l2", structures=[StringStructure("s")])
			l3 = ListStructure("l3", structures=[IntegerStructure("i")])
		
		cls = test()
		self.assertRaises(AttributeError, lambda: cls.i)
		cls.i = 3
		self.assertEquals(cls.i, 3)
		self.assertFalse(cls.i != 3)
		del cls.i
		self.assertRaises(AttributeError, lambda: cls.i)
		
		cls.s = "test"
		self.assertEquals(cls.s, "test")
		
		cls.g = ["foo", ["bar"]]
		self.assertEquals(cls.g.s, "foo")
		self.assertEquals(cls.g.g.s, "bar")
		self.assertEquals(cls.g, ["foo", ["bar"]])
		
		cls.g[0] = "oof"
		self.assertEquals(cls.g[0], "oof")
		del cls.g[0]
		self.assertRaises(AttributeError, lambda: cls.g[0])
		self.assertRaises(AttributeError, lambda: cls.g.s)
		self.assertRaises(AttributeError, lambda: cls.g.x)
		cls.g.s = "foo"
		self.assertEquals(cls.g.s, "foo")
		try:
			cls.g.x = 0
			self.fail("Assigning a non-existent member of a GroupStructure didn't fail.")
		except AttributeError, e:
			pass
		
		del cls.g.s
		try:
			del cls.g.x
			self.fail("Deleting a non-existent member of a GroupStructure didn't fail.")
		except AttributeError, e:
			pass
		
		del cls.g
		
		
		cls.l = [['abc', '\x00']]
		self.assertEquals(cls.l[0], ['abc', '\x00'])
		self.assertEquals(cls.l, [['abc', '\x00']])
		
		self.assertNotEquals(cls.l, [[]])
		self.assertNotEquals(cls.l, [])
		self.assertNotEquals(cls.l, [[], []])
		#this test differs from the above:
		#assertNotEquals(a,b) asserts not a == b, this asserts a != b
		#these are different statements
		self.assertTrue(cls.l != [])
		
		cls.l[0] = ['1', '2']
		del cls.l[0]
		self.assertEqual(len(cls.l), 0)
		cls.l[0:] = [['a', 'b'], ['c', 'd']]
		self.assertEqual(cls.l, [['a', 'b'], ['c', 'd']])
		cls.l.append(['e', 'f'])
		self.assertEqual(cls.l, [['a', 'b'], ['c', 'd'], ['e', 'f']])
		del cls.l
		
		cls.l2 = ["ab", "cd", "ef"]
		self.assertEquals(cls.l2, ["ab", "cd", "ef"])
		self.assertEquals(len(cls.l2), 3)
		cls.l2[1] = "CD"
		self.assertEquals(cls.l2, ["ab", "CD", "ef"])
		cls.l2[1:-1] = ["cd"]
		self.assertEquals(cls.l2, ["ab", "cd", "ef"])
		del cls.l2[1]
		self.assertEquals(cls.l2, ["ab", "ef"])
		self.assertEquals(len(cls.l2), 2)
		
		for i, j in zip(cls.l2, ["ab", "ef"]):
			self.assertEquals(i, j)
		self.assertEquals(cls.l2 + ["gh"], ["ab", "ef", "gh"])
		self.assertEquals(cls.l2 * 2, ["ab", "ef", "ab", "ef"])
		self.assertEquals(2 * cls.l2, ["ab", "ef", "ab", "ef"])
		self.assertTrue("ef" in cls.l2)
		self.assertFalse("ef" not in cls.l2)
		self.assertFalse("CD" in cls.l2)
		self.assertTrue("CD" not in cls.l2)
		cls.l2.append("gh")
		self.assertEqual(cls.l2, ["ab", "ef", "gh"])
		self.assertEqual(list(reversed(cls.l2)), ["gh", "ef", "ab"])
		cls.l2.reverse()
		self.assertEqual(cls.l2, ["gh", "ef", "ab"])
		cls.l2.sort()
		self.assertEqual(cls.l2, ["ab", "ef", "gh"])
		
		cls.l3 = range(10)
		self.assertEqual(cls.l3, [0,1,2,3,4,5,6,7,8,9])
		self.assertEqual(cls.l3[1:8], [1,2,3,4,5,6,7])
		self.assertEqual(cls.l3[1:8:2], [1,3,5,7])
		self.assertEqual(cls.l3.count(2), 1)
		self.assertEqual(cls.l3.pop(0), 0)
		cls.l3.insert(0,0)
		self.assertEqual(cls.l3, [0,1,2,3,4,5,6,7,8,9])
		self.assertEqual(cls.l3.index(1), 1)
		cls.l3.extend([10,11,12,13])
		self.assertEqual(cls.l3, [0,1,2,3,4,5,6,7,8,9,10,11,12,13])
		cls.l3.reverse()
		self.assertEqual(cls.l3, [13,12,11,10,9,8,7,6,5,4,3,2,1,0])
		cls.l3.remove(5)
		self.assertEqual(cls.l3, [13,12,11,10,9,8,7,6,4,3,2,1,0])
		cls.l3[0:13:2] = [13,11,9,7,4,2,0]
		self.assertEqual(cls.l3, [13,12,11,10,9,8,7,6,4,3,2,1,0])

if __name__ == '__main__':
	unittest.main()