
class StructureTest(object):
	def CanNotCreateStructure(self):
		"""
		Structure is an abstract base.
		"""
		try:
			Structure("test")
			assert False, "Was able to create the Structure class"
		except TypeError:
			pass
