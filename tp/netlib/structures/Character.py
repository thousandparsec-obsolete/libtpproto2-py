
class CharacterStructure(StringStructure):
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('size'):
			self.size = kw['size']
		else:
			self.size = 1
	
	def check(self, value):
		StringStructure.check(self, value)
		if len(value) != self.size:
			raise ValueError("Value is not the correct size! Must be length %i" % self.size)
			
	def length(self, value):
		return self.size
	
	def xstruct(self):
		if self.size == 1:
			return 'c'
		return str(self.size)+'s'
	xstruct = property(xstruct)
