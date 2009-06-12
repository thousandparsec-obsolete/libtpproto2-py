from types import IntType, LongType

from Structure import Structure

class IntegerStructure(Structure):
	sizes = {
		8: ('b', 'B', None), 
		16: ('h', 'H', 'n'),
		32: ('i', 'I', 'j'),
		64: ('q', 'Q', 'p'),
	}
	
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('size'):
			size = kw['size']
		else:
			size = 32
		
		if kw.has_key('type'):
			type = kw['type']
		else:
			type = 'signed'
		
		if not size in self.sizes.keys():
			raise ValueError("Only supported sizes are %r not %i" % (self.sizes.keys(),size))
		self.size = size

		if not type in ("signed", "unsigned", "semisigned"):
			raise ValueError("Type can only be signed, unsigned or semisigned")
		self.type = type

	def check(self, value):
		if not isinstance(value, (IntType, LongType)):
			raise ValueError("Value (%s) must be a number" % value)

		# Do a bounds check now
		if self.type == "signed":
			max = 2**(self.size-1)-1
			min = -2**(self.size-1)
		elif self.type == "unsigned":
			max = 2**self.size-1
			min = 0
		elif self.type == "semisigned":
			max = 2**self.size-2
			min = -1

		if value < min:
			raise ValueError("Value is too small! Must be bigger then %i" % min)
		
		if value > max:
			raise ValueError("Value is too big! Must be smaller then %i" % max)
		
		return True
			
	def length(self, value):
		return self.size / 8

	def xstruct(self):
		if self.type == "signed":
			xstruct = self.sizes[self.size][0]
		elif self.type == "unsigned":
			xstruct = self.sizes[self.size][1]
		elif self.type == "semisigned":
			xstruct = self.sizes[self.size][2]
		return xstruct
	xstruct = property(xstruct)

