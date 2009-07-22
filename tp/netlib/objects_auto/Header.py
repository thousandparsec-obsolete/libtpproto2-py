
import copy

from Packet import Packet
import structures

def _makeHeader(version):
	class Header(Packet):
		name = "Header"
		VERSION = version
		_structures = [
			structures.CharacterStructure("version", "Protocol Version", size=4),
			structures.IntegerStructure("sequence",  "Sequence Number",  size=32, type="unsigned"),
			structures.IntegerStructure("type",      "Packet Type",      size=32, type="unsigned"),
			structures.IntegerStructure("length",    "Length of Packet", size=32, type="unsigned"),
		]
	
		def __init__(self, *arguments, **kw):
			if len(arguments) == 0:
				# We are building a packet from the wire.
				raise NotImplimented("Not finished yet...")
			else:
				Packet.__init__(self, self.VERSION, arguments[0], self.__class__._id, 0, *arguments[1:], **kw)
		
		def set_length(self, value):
			return
		def get_length(self):
			l = 0
			for structure in self.structures:
				if structure.name == 'length':
					value = None
				else:
					value = getattr(self, structure.name)
				l += structure.length(value)
			return l
		length = property(get_length, set_length)
	return Header