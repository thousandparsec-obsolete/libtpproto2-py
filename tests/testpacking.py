#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

import tp.netlib.parser as parser

class TestParser(unittest.TestCase):

	data = "\x54\x50\x30\x33\x00\x00\x00\x03\x00\x00\x00\x1a\x00\x00\x00\x10\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x03\xe8"

	objects = parser.parseFile("tp/netlib/protocol3.xml")
	
	packet = objects.Features()
	packet.unpack(data)

	print packet
	print packet._length
