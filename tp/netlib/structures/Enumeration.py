from types import StringTypes, IntType, LongType

from Integer import IntegerStructure

class EnumerationStructure(IntegerStructure):
	def __init__(self, *args, **kw):
		IntegerStructure.__init__(self, *args, **kw)

		if kw.has_key('values'):
			self.values = kw['values']

			for name, id in self.values.items():
				try:
					IntegerStructure.check(self, id)
				except ValueError, e:
					raise ValueError("Id's %s doesn't meet the requirements %s" % (name, e))

				if not isinstance(name, StringTypes):
					raise TypeError("Name of %i must be a string!" % id)
		
	def check(self, value):
		if isinstance(value, (IntType, LongType)):
			if value in self.values.values():
				return True
			else:
				raise ValueError("Number %s not in enumeration values." % (value,))

		elif isinstance(value, StringTypes):
			if value in self.values:
				return	True
			else:
				raise ValueError("String %s not in enumeration keys." % (value,))
		else:
			raise TypeError("Value must be an integer or string.")
