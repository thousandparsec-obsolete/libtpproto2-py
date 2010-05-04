
from tp.netlib.xstruct import pack, unpack, hexbyte

class PacketMeta(type):
	def get_structures(cls):
		parent = cls.__bases__[0]
		r = []
		if parent != Packet:
			r += parent.structures
		if cls.__dict__.has_key('_structures'):
			r += cls._structures
		return r

	def set_structures(cls, value):
		cls._structures = value
	structures = property(get_structures, set_structures,"""\
		get_structures() -> [<structure>,]

		A list of structures. Cascades up the parent classes.

		For example,

		>>>class A:
		>>> __metaclass__ = PacketMeta
		>>>	pass
		>>>
		>>>A.structure = [1,]
		>>>
		>>>class B(A):
		>>>	pass
		>>>
		>>>B.structure = [2,]
		>>>
		>>>print B.structure
		[<structure 0x123456>, <structure 0x7890123>,]
		""")

	def __str__(self):
		#This doesn't work because some packets have a "name" structure.
		#return "<dynamic-class '%s' at %s>" % (self.name, hex(id(self)))
		return "<dynamic-class at %s>" % hex(id(self))
	__repr__ = __str__

class Packet(object):
	__metaclass__ = PacketMeta
	name = "Root Packet"

	def __init__(self, *arguments):
		self.structures = self.__class__.structures

		if len(arguments) == 0:
			return

		if len(arguments) < len(self.structures):
			raise ValueError("Not enough arguments given (received %s rather than %s)" % (len(arguments), len(self.structures)))
		
		arguments = list(arguments)
		
		# Check each argument is valid
		for structure in self.structures:
			argument = arguments.pop(0)
			structure.check(argument)
			structure.__set__(self, argument)
			setattr(self, structure.name, argument)

	def xstruct(self):
		xstruct = ""
		for structure in self.structures:
			xstruct += structure.xstruct
		return xstruct
	xstruct = property(xstruct)
	
	def pack(self):
		return ''.join([structure.pack(self) for structure in self.structures])
	
	def unpack(self, string):
		for structure in self.structures:
			string = structure.unpack(self, string)
		return string

