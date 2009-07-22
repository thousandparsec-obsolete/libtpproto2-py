from types import *
import xml.dom.minidom
from xml.parsers.expat import ExpatError

# Squash warnings about hex/oct
import warnings

# Local Imports
import structures
import objects_auto

convert = {
	'id':	int,
}

class Objects(object):
	"""This class acts as a container for the protocol datatypes."""
	def __init__(self):
		#copy the pre-written base objects
		for name in dir(objects_auto):
			if not name.startswith('_'):
				setattr(self, name, getattr(objects_auto, name))

objects = Objects()

class Parameter(object):
	usestruct = []
	descstruct = []
	name = ""
	type = -1

class DescStructure(structures.GroupStructure):
	def __init__(self, *args, **kw):
		if kw.has_key('typefield'):
			self.typefield = kw['typefield']
		if kw.has_key('ref'):
			self.ref = kw['parametersets'][kw['ref']]
		kw['structures'] = []
		
		structures.GroupStructure.__init__(self, *args, **kw)
	
	def check(self, value):
		return True
	
	def __set__(self, obj, value):
		self.structures = self.ref[getattr(obj.group, self.typefield)].descstruct
		try:
			structures.GroupStructure.check(self, value)
			structures.GroupStructure.__set__(self, obj, value)
		except:
			self.structures = []
			raise
		self.structures = []

	def __get__(self, obj, objcls):
		self.structures = self.ref[getattr(obj.group, self.typefield)].descstruct
		try:
			value = structures.GroupStructure.__get__(self. obj. objcls)
		except:
			self.structures = []
			raise
		self.structures = []
		return value

	def __delete__(self, obj):
		self.structures = self.ref[getattr(obj.group, self.typefield)].descstruct
		try:
			structures.GroupStructure.__delete__(self. obj)
		except:
			self.structures = []
			raise
		self.structures = []


def getText(nodes):
	"""Pull the text out of <tag>text</tag>"""
	for node in nodes:
		if node.nodeType == node.TEXT_NODE:
			return node.data
		elif node.nodeType != node.COMMENT_NODE:
			raise ValueError("Unexepcted node %s while searching for text." % node.nodeName)
	return ""

class Parser(object):
	def parseFile(self, file):
		"""Opens the file and return the protocol described by it."""
		self.objects = Objects()
		self.parametersets = {}
		try:
			document = xml.dom.minidom.parse(file)
		except ExpatError, e:
			raise ValueError("Error parsing %s: %s" % (file, e))
		root = document.documentElement
		if root.nodeName != "protocol":
			raise ValueError("Outermost tag of %s is %s, not protocol" % (file, root.nodeName))
		if str(root.attributes['version'].value) == 'TP03':
			self.objects.Header = objects_auto._makeHeader('TP03')
		elif str(root.attributes['version'].value) == 'TP04':
			self.objects.Header = objects_auto._makeHeader('TP\x04\x00')
		for child in root.childNodes:
			if child.nodeName == 'packet':
				self.buildPacket(child)
			elif child.nodeName == 'parameterset':
				name = str(child.attributes['name'].value)
				self.parametersets[name] = self.buildParameterSet(child)
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]: #text nodes are okay
				raise ValueError("Unrecognized tag in protocol: %s" % child.nodeName)
		return self.objects

	def buildPacket(self, packet):
		structures = []
		
		try:
			name = packet.attributes['name'].value
		except KeyError:
			raise ValueError("Packet has no name!")
		
		base = self.objects.Packet
		if 'base' in packet.attributes.keys():
			try:
				base = getattr(self.objects, packet.attributes['base'].value)
			except AttributeError:
				raise ValueError("Packet base %s of %s does not exist" % (packet.attributes['base'].value, name))
			
		if hasattr(self.objects, name):
			print "Skipping %s because it's pre-written." % name
			return
		
		class NewPacket(base):
			pass
		
		for attribute in packet.attributes.keys():
			value = packet.attributes[attribute].value
			if attribute in convert:
				value = convert[attribute](value)
			setattr(NewPacket, '_' + attribute, value)
		
		for child in packet.childNodes:
			if child.nodeName == 'structure':
				structures = self.buildStructureList(child, name)
			elif child.nodeName in ['direction', 'failtype', 'description', 'note', 'longname']:
				pass
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in packets: %s" % child.nodeName)
		
		for structure in structures:
			setattr(NewPacket, structure.name, structure)
		setattr(NewPacket, 'structures', structures)
		
		setattr(self.objects, name, NewPacket)

	def buildStructureList(self, structure, packetName = None):
		"""Parse a structure node and construct a list of all the structures inside"""
		types = ("string", "character", "integer", "list", "group", "enumeration", "datetime", "descparameter")
		list = []
		for child in structure.childNodes:
			#if it's a recognized structure
			if child.nodeName in types:
				list.append(self.buildStructure(child))
			elif child.nodeName == 'useparameters':
				if packetName == None:
					raise ValueError("useparameters tag not in toplevel structure of a packet!")
				else:
					self.buildUseParameters(child, packetName)
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in structure: %s" % child.nodeName)
		return list

	def buildStructure(self, structure):
		"""Translate a node into a structure."""
		type = structure.nodeName.title()
		attributes = {}
		for child in structure.childNodes:
			if child.nodeName in ['name', 'longname', 'description', 'note', 'example']:
				key = str(child.nodeName)
				value = getText(child.childNodes)
				attributes[key] = value
			elif child.nodeName == 'values':
				attributes['values'] = self.buildValues(child)
			elif child.nodeName == 'structure':
				attributes['structures'] = self.buildStructureList(child)
			elif child.nodeName == 'subtype':
				pass #not sure if we need to do anything with this
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in %s: %s" % (type, child.nodeName))
		for attribute in structure.attributes.keys():
			key = str(attribute)
			if key == 'size':
				value = int(structure.attributes[attribute].value)
			else:
				value = str(structure.attributes[attribute].value)
			attributes[key] = value
		
		if type == 'Descparameter':
			attributes['parametersets'] = self.parametersets
			return DescStructure(**attributes)
		else:
			return getattr(structures, type + "Structure")(**attributes)

	def buildValues(self, node):
		"""Builds the value list that is used in enumeration structures."""
		values = {}
		for child in node.childNodes:
			if child.nodeName == 'value':
				name = str(child.attributes['name'].value)
				if child.attributes['id'].value.startswith('0x'):
					id = int(child.attributes['id'].value, 16)
				else:
					id = int(child.attributes['id'].value)
				values[name] = id
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in values: %s" % child.nodeName)
		return values

	def buildParameterSet(self, node):
		parameters = {}
		for child in node.childNodes:
			if child.nodeName == 'parameter':
				type = int(child.attributes['type'].value)
				parameters[type] = self.buildParameter(child)
			elif child.nodeName in ['longname', 'description']:
				pass #don't really use these, but they're valid.
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in parameterset: %s" % child.nodeName)
		return parameters

	def buildParameter(self, node):
		name = str(node.attributes['name'].value)
		type = int(node.attributes['type'].value)
		parameter = Parameter()
		for child in node.childNodes:
			if child.nodeName in ['usestruct', 'descstruct']:
				for structNode in child.childNodes:
					if structNode.nodeName == 'structure':
						structure = self.buildStructureList(structNode)
						setattr(parameter, child.nodeName, structure) #set usestruct or descstruct
					elif structNode.nodeType not in [structNode.TEXT_NODE, structNode.COMMENT_NODE]:
						raise ValueError("Unrecognized tag in usestruct: %s" % structNode.nodeName)
			elif child.nodeName in ['longname', 'description', 'note']:
				pass #don't really use these, but they're valid.
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in parameter: %s" % child.nodeName)
		setattr(objects, name, parameter)
		return parameter

	def buildUseParameters(self, node, packetName):
		"""The useparameters field actually defines how a description class will add extra structures to the class.
		This function adds a build method to the description to return an augmented version of the class in question"""
		try:
			ref = node.attributes['ref'].value
		except KeyError:
			raise ValueError("Useparameters has no ref!")
		parameters = self.parametersets[ref]
		attributes = {}
		for child in node.childNodes:
			if child.nodeName in ['name', 'longname', 'description', 'typefield']:
				key = str(child.nodeName)
				value = getText(child.childNodes)
				attributes[key] = value
			elif child.nodeName == 'typeframe':
				try:
					name = child.attributes['name'].value
				except KeyError:
					raise ValueError("Typeframe has no name!")
				objects = self.objects #so this can be accessed in the build method
				getter = self.buildGetter(child)
				def build(self):
					base = getattr(objects, packetName)
					class ExtendedPacket(base):
						pass
					for name, type, description in getter(self):
						parameter = structures.GroupStructure(name=name, structures=parameters[type].usestruct, description=description)
						ExtendedPacket.structures = [parameter]
						setattr(ExtendedPacket, name, parameter)
					return ExtendedPacket
				setattr(getattr(self.objects, name), 'build', build)
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in useparameters: %s" % child.nodeName)

	def buildGetter(self, parent):
		for child in parent.childNodes:
			if child.nodeName == 'getlist':
				try:
					name = child.attributes['name'].value
				except KeyError:
					raise ValueError("getlist has no name!")
				getter = self.buildGetter(child)
				def get(obj):
					result = []
					for i in getattr(obj, name):
						result += getter(i)
					return result
			elif child.nodeName == 'getfield':
				try:
					name = child.attributes['name'].value
				except KeyError:
					raise ValueError("getlist has no name!")
				def get(obj):
					return [(getattr(obj, 'name'), getattr(obj, 'type'), getattr(obj, 'description'))]
			elif child.nodeType not in [child.TEXT_NODE, child.COMMENT_NODE]:
				raise ValueError("Unrecognized tag in %s: %s" % (parent.nodeName, child.nodeName))
		return get

def parseFile(file):
	parser = Parser()
	return parser.parseFile(file)