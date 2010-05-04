from types import TupleType, ListType

from tp.netlib.xstruct import pack, unpack
from Structure import Structure
from Group import GroupStructure

class ListStructure(GroupStructure):
	class ListProxy(object):
		def __init__(self, list, obj, objcls):
			self.list = list
			self.obj    = obj
			self.objcls = objcls
		
		def __eq__(self, other):
			return list(self) == other
		
		def __ne__(self, other):
			return not self.__eq__(other)
		
		def __ge__(self, other):
			return list(self).__ge__(other)
		
		def __gt__(self, other):
			return list(self).__gt__(other)
		
		def __le__(self, other):
			return list(self).__le__(other)
		
		def __lt__(self, other):
			return list(self).__lt__(other)
		
		def __len__(self):
			return len(getattr(self.obj, "_" + self.list.name))
		
		def __getitem__(self, position):
			if isinstance(position, slice):
				positions = range(len(self)).__getitem__(position)
				return [self.__getitem__(i) for i in positions]
			else:
				if len(self.list.structures) != 1:
					return getattr(self.obj, "_" + self.list.name)[position].group
				else:
					return getattr(self.obj, "_" + self.list.name)[position].group[0]

		def __setitem__(self, position, value):
			if isinstance(position, slice):
				positions = range(len(self)).__getitem__(position)
				if(len(positions) != len(value)):
					raise ValueError("attempt to assign sequence of size %s to extended slice of size %s" % (len(value), len(positions)))
				for position, value in zip(positions, value):
					self.__setitem__(position,value)
			else:
				if len(self.list.structures) != 1:
					getattr(self.obj, "_" + self.list.name)[position].group = value
				else:
					getattr(self.obj, "_" + self.list.name)[position].group[0] = value
	
		def __delitem__(self, position):
			del getattr(self.obj, "_" + self.list.name)[position]
		
		def __iter__(self):
			copy = [self[i] for i in range(len(self))]
			for i in copy:
				yield i
		
		def __add__(self, other):
			return list(self) + other
		
		def __mul__(self, other):
			return list(self) * other
		
		def __rmul__(self, other):
			return other * list(self)
		
		def __contains__(self, element):
			return element in list(self)
		
		def __getslice__(self, i, j):
			return list(self).__getslice__(i, j)
		
		def __setslice__(self, i, j, values):
			containers = []
			for value in values:
				if len(self.list.structures) != 1:
					self.list.check([value])
					container = self.list.Container(self.obj)
					container.group = value
					containers.append(container)
				else:
					self.list.check([value])
					container = self.list.Container(self.obj)
					container.group = [value]
					containers.append(container)
			getattr(self.obj, "_" + self.list.name).__setslice__(i, j, containers)
		
		def __reversed__(self):
			return reversed(list(self))
		
		
		def append(self, value):
			container = self.list.Container(self.obj)
			self.list.check([value])
			if len(self.list.structures) != 1:
				container.group = value
			else:
				container.group = [value]
			getattr(self.obj, "_" + self.list.name).append(container)
		
		def count(self, value):
			return list(self).count(value)
		
		def extend(self, values):
			for value in values:
				self.append(value)
		
		def index(self, value):
			return list(self).index(value)
		
		def insert(self, index, value):
			container = self.list.Container(self.obj)
			self.list.check([value])
			if len(self.list.structures) != 1:
				container.group = value
			else:
				container.group = [value]
			getattr(self.obj, "_" + self.list.name).insert(index, container)
		
		def pop(self, index):
			if len(self.list.structures) != 1:
				return getattr(self.obj, "_" + self.list.name).pop(index).group
			else:
				return getattr(self.obj, "_" + self.list.name).pop(index).group[0]
		
		def remove(self, value):
			self.pop(self.index(value))
		
		def reverse(self):
			getattr(self.obj, "_" + self.list.name).reverse()
		
		def sort(self):
			for index, value in enumerate(sorted(list(self))):
				self[index] = value
		
	def __init__(self, *args, **kw):
		GroupStructure.__init__(self, *args, **kw)
		
		class Container(object):
			group = GroupStructure("group", structures=self.structures)
			
			def __init__(self, parent):
				self.parent = parent
		
		self.Container = Container
		
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
		return True
	
	def length(self, list):
		length = 4
		for item in list:
			if len(self.structures) != 1:
				for i in xrange(0, len(self.structures)):
					length += self.structures[i].length(item[i])
			else:
				length += self.structures[0].length(item)
		return length

	def xstruct(self):
		xstruct = "["
		for struct in self.structures:
			xstruct += struct.xstruct
		return xstruct+"]"
	xstruct = property(xstruct)
	name = ''
	
	def pack(self, obj):
		data = getattr(obj, "_" + self.name)
		size = len(data)
		string = pack('I', size)
		for i in data:
			for structure in self.structures:
				string += structure.pack(i)
		return string
	
	def unpack(self, obj, string):
		size, string = unpack('I', string)
		size = size[0]
		data = []
		for i in xrange(size):
			data.append(self.Container(obj))
			for structure in self.structures:
				string = structure.unpack(data[-1], string)

		setattr(obj, "_" + self.name, data)
		
		return string
	
	def __set__(self, obj, values):
		self.check(values)
		setattr(obj, "_" + self.name, [])
		for value in values:
			if len(self.structures) != 1:
				container = self.Container(obj)
				container.group = value
				getattr(obj, "_" + self.name).append(container)
			else:
				container = self.Container(obj)
				container.group = (value,)
				getattr(obj, "_" + self.name).append(container)

	def __get__(self, obj, objcls):
		if obj is None:
			return self
		
		return self.ListProxy(self, obj, objcls)

	def __delete__(self, obj):
		delattr(obj, "_" + self.name)

