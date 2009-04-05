
import time
from datetime import datetime
class DateTimeStructure(Structure):
	sizes = {
		32: ('t'),
		64: ('T'),
	}

	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)
		if kw.has_key('size'):
			size = kw['size']
		else:
			size = 64
		
		if not size in self.sizes.keys():
			raise ValueError("Only supported sizes are %r not %i" % (self.sizes.keys(),size))
		self.size = size
	
	def check(self, value):
		if not isinstance(value, datetime):
			raise ValueError("Value must be a datetime")

		i = time.mktime(value.timetuple())
		if i < 0:
			raise ValueError("Value is too small! Must be bigger then %i" % min)
		
		if i > 2**self.size-1:
			raise ValueError("Value is too big! Must be smaller then %i" % max)
	
	def length(self, value):
		return self.size / 8
	
	def xstruct(self):
		xstruct = self.sizes[self.size][0]
	xstruct = property(xstruct)
