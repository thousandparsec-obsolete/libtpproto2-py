
class ListStructure(GroupStructure):
	def check(self, list):
		if not isinstance(list, (TupleType, ListType)):
			raise ValueError("Value must be a list or tuple")
		
		for item in list:
			if len(self.structures) != 1:
				if not isinstance(item, (TupleType, ListType)):
					raise ValueError("Value items must be a list or tuple not %r" % type(item))

				if len(item) != len(self.structures):
					raise ValueError("Value item was not the correct size (was %i must be %i)" % (len(item), len(self.structures)))
			
				for i in xrange(0, len(self.structures)):
					self.structures[i].check(item[i])
			else:
				self.structures[0].check(item)
	
	def length(self, list):
		length = 4
		for item in list:
			if len(self.structures) != 1:
				for i in xrange(0, len(self.structures)):
					length += self.structures[i].length(item[i])
			else:
				length += self.structures[0].check(item)
		return length

	def xstruct(self):
		xstruct = "["
		for struct in self.structures:
			xstruct += struct.xstruct
		return xstruct+"]"
	xstruct = property(xstruct)

