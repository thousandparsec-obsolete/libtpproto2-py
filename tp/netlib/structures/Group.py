
class GroupStructure(Structure):
	class GroupProxy(object):
		def __init__(self, group, obj, objcls):
			self.group  = group
			self.obj    = obj
			self.objcls = objcls

		def __eq__(self, other):
			l = []
			for i, structure in enumerate(self.group.structures):
				l.append(self[i])
			return l == other

		def __getitem__(self, position):
			return self.group.structures[position].__get__(self.obj, self.objcls)

		def __setitem__(self, position, value):
			return self.group.structures[position].__set__(self.obj, value)
	
		def __delitem__(self, position):
			return self.group.structures[position].__delete__(self.obj)

		def __getattr__(self, name):
			for i, structure in enumerate(self.group.structures):
				if structure.name == "__%s_%s" % (self.group.name, name):
					return self[i]
			raise AttributeError("No such attribute %s" % name)

		def __setattr__(self, name, value):
			if name in ("group", "obj", "objcls"):
				object.__setattr__(self, name, value)
			else:
				for i, structure in enumerate(self.group.structures):
					if structure.name == "__%s_%s" % (self.group.name, name):
						self[i] = value
						return
				raise AttributeError("No such attribute %s" % name)
		def __delattr__(self, name):
			for i, structure in enumerate(self.group.structures):
				if structure.name == name:
					del self[i]
					return
			raise AttributeError("No such attribute %s" % name)
	
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('structures'):
			structures = kw['structures']
		else:
			structures = []
		
		if not isinstance(structures, (TupleType, ListType)):
			raise ValueError("Argument must be a list or tuple")

		for structure in structures:
			if not isinstance(structure, Structure):
				raise ValueError("All values in the list must be structures!")

			# Rewrite the names so they don't clash
			structure.name = "__%s_%s" % (self.name, structure.name)

		self.structures = structures

	def check(self, values, checkall=True):
		if not isinstance(values, (TupleType, ListType)):
			raise ValueError("Value must be a list or tuple")
		
		if len(values) != len(self.structures):
			raise ValueError("Value is not the correct size, was %i must be %i" % (len(list), len(self.structures)))

		if checkall:
			for i in xrange(0, len(self.structures)):
				self.structures[i].check(values[i])

	def length(self, list):
		length = 0
		for i in xrange(0, len(self.structures)):
			length += self.structures[i].length(item[i])
		return length
	
	def xstruct(self):
		for struct in self.structures:
			xstruct += struct.xstruct
	xstruct = property(xstruct)

	def __set__(self, obj, value):
		self.check(value, False)
		value = list(value)
		for structure in self.structures:
			structure.__set__(obj, value.pop(0))

	def __get__(self, obj, objcls):
		return self.GroupProxy(self, obj, objcls)

	def __del__(self, obj):
		for structure in self.structures:
			structures.__del__(obj)