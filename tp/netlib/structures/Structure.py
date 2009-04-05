
class Structure(object):
	def __init__(self, name=None, longname="", description="", example="", **kw):
		if name is None:
			raise ValueError("Name did not exist!")
		
		self.name = name
		self.longname = longname
		self.description = description
		self.example = example

		if self.__class__ == Structure:
			raise TypeError("Structure is an Abstract base class!")
	
	def check(self, value):
		"""\
		check(value) -> None

		This function will check if an argument is valid for this structure.
		If the argument is not valid it should throw a ValueError exception.
		"""
		raise SyntaxError("Not Implimented")

	def length(self, value):
		"""\
		length(value) -> int

		This function will return the length (number of bytes) of the encoded
		version of the value.
		"""
		raise SyntaxError("Not Implimented")

	def xstruct(self):
		"""\
		xstruct() -> string

		Returns the xstruct value for this structure.
		"""
		raise SyntaxError("Not Implimented")
	xstruct = property(xstruct)

	def __str__(self):
		return "<%s %s %s>" % (self.__class__.__name__.split('.')[-1], hex(id(self)), self.name)
	__repr__ = __str__

	def __set__(self, obj, value):
		self.check(value)
		setattr(obj, "__"+self.name, value)

	def __get__(self, obj, objcls):
		try:
			return getattr(obj, "__"+self.name)
		except AttributeError, e:
			raise AttributeError("No value defined for %s" % self.name)

	def __delete__(self, obj):
		delattr(obj, "__"+self.name)

