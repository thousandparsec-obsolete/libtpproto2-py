
class StringStructureTest(object):
	def setup(self):
		class StringObject(object):
			s = StringStructure('s')
		
		str = StringObject()

	def TestEmptyOnCreation(self):
		try:
			str.s
			assert False, "The attribute was not empty!"
		except AttributeError, e:
			assert str(e).find("empty") != -1

	def TestAssignment(self):
		str.s = "test"
		assert str.s == "test"

	def TestNonStringAssignment(self):
		for crap in [1, 6L, [], (), str]:
			try:
				str.s = crap
				assert False, "Was able to assign %r to a string attribute!" % crap
			except TypeError, e:
				pass

