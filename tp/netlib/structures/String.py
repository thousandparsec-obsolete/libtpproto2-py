class StringStructure(Structure):
	def check(self, value):
		if not isinstance(value, StringTypes):
			raise ValueError("Value must be a string type")

	def length(self, value):
		return 4+len(value)

	xstruct = 'S'

class StringStructureTest(object):
	def test(self):
		class StringObject(object):
			s = StringStructure('s')
		
		str = StringObject()
		# Check that the default value is empty
		try:
			str.s
			assert False
		except AttributeError, e:
			pass

		# Check assignment is a value
		str.s = "test"
		assert str.s == "test"

		# Check the length
		assert StringObject.s.length(str.s) == 8

		# Check that you can't assign crap values
		for crap in [1, 6L, [], (), str]:
			try:
				str.s = crap
				assert False, "Was able to assign %r to a string attribute!" % crap
			except TypeError, e:
				pass

