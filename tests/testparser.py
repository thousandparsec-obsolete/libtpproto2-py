#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'tp/netlib')

import unittest
from datetime import datetime

import parser

class TestParser(unittest.TestCase):
	
	def test_protocol3(self):
		objects = parser.parseFile("tp/netlib/protocol3.xml")
		
		packet = objects.Okay(0, "")
		self.assertEquals(packet.xstruct, "4sIIIS")
		self.assertEquals(packet.pack(), 'TP03' '\x00\x00\x00\x00' '\x00\x00\x00\x00' '\x00\x00\x00\x04' '\x00\x00\x00\x00')
		
		packet = objects.Fail(0, "Frame", "Error!", [])
		self.assertEquals(packet.xstruct, "4sIIIIS")
		
		packet = objects.GetObjectIDsByPos(0, (0, 0, 0), 0)
		self.assertEquals(packet.xstruct, "4sIIIqqqQ")
		
	
	def test_protocol4(self):
		objects = parser.parseFile("tp/netlib/protocol.xml")
		
		packet = objects.Okay(0, "\x01")
		self.assertEquals(packet.xstruct, "4sIIIS")
		self.assertEquals(packet.pack(), 'TP' '\x04' '\x00' '\x00\x00\x00\x00' '\x00\x00\x00\x00' '\x00\x00\x00\x05' '\x00\x00\x00\x01' '\x01')
		
		packet = objects.Fail(0, "Frame", "Error!", [])
		self.assertEquals(packet.xstruct, "4sIIIIS[iI]")
		
		packet = objects.GetObjectIDsByPos(0, (0, 0, 0), 0)
		self.assertEquals(packet.xstruct, "4sIIIqqqQ")
		
		packet = objects.Object(0, 0, 0, '', '', 0, [], 0, '\x00'*16)
		
		packet = objects.ObjectDesc(0, 0, '', '', 0, [])
		packet = objects.ObjectDesc(0, 0, '', '', 0, [[0, '', '', [] ]] )
		
		packet = objects.ObjectDesc(0, 0, '', '', 0, [[0, '', '', [['Parameter', 0, 'Description', [] ]] ]] )
		packet = packet.build()(0, 0, 0, '', '', 0, [], 0, '\x00'*16, [[0, 0, 0], 0])
		
		self.assertEquals(packet.Parameter.position, [0,0,0])
		self.assertEquals(packet.Parameter.relative, 0)
		del packet.Parameter
		
		
		
		packet = objects.ObjectDesc(0, 0, '', '', 0, [[0, '', '', [['Parameter1', 0, 'Description', [] ], ['Parameter2', 4, 'Description', [0] ]] ]] )
	
	def test_verification(self):
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol001.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol002.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol003.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol004.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol005.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol006.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol007.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol008.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol009.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol010.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol011.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol012.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol013.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol014.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol015.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol016.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol017.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol018.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol019.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol020.xml')
		self.assertRaises(ValueError, parser.parseFile, 'tests/xml/testprotocol021.xml')

if __name__ == '__main__':
	unittest.main()
