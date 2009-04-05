class EnumerationStructure(IntegerStructure):
	def __init__(self, *args, **kw):
		IntegerStructure.__init__(self, *args, **kw)

		if kw.has_key('values'):
			values = kw['values']

			for id, name in self.values.items():
				try:
					IntegerStructure.check(self, id)
				except ValueError, e:
					raise ValueError("Id's %i doesn't meet the requirements %s" % (type(id), e))

				if not isinstance(value, StringTypes):
					raise ValueError("Name of %i must be a string!" % id)
		
	def check(self, value):
		if isinstance(value, (IntType, LongType)):
			if value in self.values.keys():
				return	

		if isinstance(value, StringTypes):
			if value in self.values.values():
				return	

		raise ValueError("Value must be a number")

			
	def length(self, value):
		return self.size / 8

	def xstruct(self):
		if self.type == "signed":
			xstruct = self.sizes[self.size][0]
		elif self.type == "unsigned":
			xstruct = self.sizes[self.size][1]
		elif type == "semesigned":
			xstruct = self.sizes[self.size][2]
		return xstruct
	xstruct = property(xstruct)
