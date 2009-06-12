from types import StringType, StringTypes, UnicodeType

from Structure import Structure


class StringStructure(Structure):
	def check(self, value):
		if not isinstance(value, StringTypes):
			raise ValueError("Value must be a string type")
		return True

	def length(self, value):
		return 4+len(unicode(value).encode('utf-8'))

	xstruct = 'S'