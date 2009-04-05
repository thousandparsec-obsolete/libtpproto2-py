
class CharacterTest(StringTest):
	def setup(self):
		class CharacterObject(object):
			s = CharacterStructure('s', length=4)
		
		str = CharacterObject()

	def TestAssignmentIncorrectLength(self):
		# Character structure only accepts characters of the length specified
		try:
			str.s = "t"
			assert False, "Was able to assign length != 4"
		except TypeError, e:
			pass
		
		try:
			str.s = "ttttttt"
			assert False, "Was able to assign length != 4"
		except TypeError, e:
			pass
