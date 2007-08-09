

import objects

class Progress(object):
	"""\
	This class indicated that some progress has been made in downloading a
	sequence.
	"""
	def __init__(self, number=None, of=None):
		if of is None:
			if not number is None:
				raise TypeError("When giving the 'number' argument, you must also provide an 'of' argument")
		elif not isinstance(of, (int, long)):
			raise TypeError("The 'of' argument must be integer or None")
		self.of = of

		if not isinstance(number, (type(None), int, long)):
			raise TypeError("The 'number' argument must be an integer or None")
		if number > of:
			raise TypeError("The 'number' argument must be less than or equal to the 'of' argument")
		self.number = number	

	def __eq__(self, other):
		return (other is None) or (other is False)

def getlistarg(name, *args, **kw):
	"""
	Pick out ids from the *args/**kw (plus do some sanity checking).
	"""
	# Check for the plural version (which should be a list).
	if kw.has_key(name+'s'):
		rarg = kw[name+'s']
	# Check for the single version
	elif kw.has_key(name):
		rarg = [name]
	# Check for the argument in first position
	elif len(args) == 1 and hasattr(args[0], '__getitem__'):
		rarg = args[0]
	# Else use the all the arguments
	else:
		rarg = args

	if not hasattr(rarg, '__getitem__'):
		raise TypeError('Argument %s must have a __getitem__ method' % name)

	for arg in rarg:
		if not isinstance(arg, (int, long)):
			raise TypeError("All %ss must be intergers! Got '%r'" % (name, arg))
	return rarg

def getidsarg(*args, **kw):
	"""
	Pick out ids from the *args/**kw (plus do some sanity checking).
	"""
	return getlistarg('id', *args, **kw)

def getslotsarg(*args, **kw):
	"""
	Pick out the slots from *args/**kw (plus do some sanity checking).
	"""
	return getlistarg('slot', *args, **kw)

import socket

from common import Connection
class ClientConnection(Connection):
	"""
	Now with thread safe goodness! *Yay*!
	Now with readable and understandable code! *Yay*
	"""
	def setup(self, host, port=None, debug=False, proxy=None):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		hoststring = host
		self.proxy = None
		
		if hoststring.startswith("tphttp://") or hoststring.startswith("tphttps://"):
			hoststring = hoststring[2:]

		if hoststring.startswith("http://") or hoststring.startswith("https://"):
			import urllib
			opener = None

			# use enviroment varibles
			if proxy == None:
				opener = urllib.FancyURLopener()
			elif proxy == "":
				# Don't use any proxies
				opener = urllib.FancyURLopener({})
			else:
				if hoststring.startswith("http://"):
					opener = urlib.FancyURLopener({'http': proxy})
				elif hoststring.startswith("https://"):
					opener = urlib.FancyURLopener({'https': proxy})
				else:
					raise "URL Error..."

			import random, string
			url = "/"
			for i in range(0, 12):
				url += random.choice(string.letters+string.digits)

			o = opener.open(hoststring + url, "")
			s = socket.fromfd(o.fileno(), socket.AF_INET, socket.SOCK_STREAM)

##			# Read in the headers
##			buffer = ""
##			while not buffer.endswith("\r\n\r\n"):
##				print "buffer:", repr(buffer)
##				try:
##					buffer += s.recv(1)
##				except socket.error, e:
##					pass
##			print "Finished the http headers..."

		else:
			if hoststring.startswith("tp://") or hoststring.startswith("tps://"):
				if hoststring.startswith("tp://"):
					host = hoststring[5:]
					if not port:
						port = 6923
				elif hoststring.startswith("tps://"):
					host = hoststring[6:]
					if not port:
						port = 6924

				if host.count(":") > 0:
					host, port = host.split(':', 1)
					port = int(port)
			else:
				if hoststring.count(":") > 0:
					host, port = hoststring.split(':', 1)
					port = int(port)
				else:
					host = hoststring

					if not port:
						port = 6923

			print "Connecting to", host, type(host), port, type(port)

			s = None
			for af, socktype, proto, cannoname, sa in \
					socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):

				try:
					s = socket.socket(af, socktype, proto)
					if debug:
						print "Trying to connect to connect: (%s, %s)" % (host, port)

					s.connect(sa)
					break
				except socket.error, msg:
					if debug:
						print "Connect fail: (%s, %s)" % (host, port)
					if s:
						s.close()

					s = None
					continue

			if not s:
				raise socket.error, msg

			if hoststring.startswith("tps://"):
				print "Creating SSL wrapper...."
				s = SSLWrapper(s)

		self.hoststring = hoststring
		self.host = host
		self.port = port

		Connection.setup(self, s, debug=debug)

	def _okfail(self, request):
		"""
		Deal with a Okay or Fail return.
		"""
		for seq in self._sendFrame(request):
			if seq == None:
				yield seq

		for p in self._recvFrame(seq):
			if p == None:
				yield p

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			yield True, p.s
		elif isinstance(p, objects.Fail):
			yield False, p.s
		else:
			raise IOError("Received a bad packet (was %r)" % p)

	def _getsingle(self, request, type):
		"""
		Deal with a Fail or give packet type return.
		"""
		for seq in self._sendFrame(request):
			if seq == None:
				yield seq

		for p in self._recvFrame(seq):
			if p == None:
				yield p

		if isinstance(p, type):
			yield p
		elif isinstance(p, objects.Fail):
			yield False, p.s

		# We got a bad packet
		else:
			raise IOError("Received a bad packet (was %r)" % p)

	def _getmany(self, request, type):
		"""\
		Deal with a Sequence of a given packet type return.

		It will,
			yield None,     if no information
			yield Progress, if some progress has been made (Progress instances == None)
			yield tuple,    if the get failed for a reason
			yield list,     if the get returned some information

		Simple way to do this in "blocking" mode:
			for result in connection.getmany(12, <type>):
				pass
			if failed(result):
				print "The command failed :/", result[1]
			print "The command worked!", r

		You don't need a sleep in the for loop because the socket is blocking and 
		hence there will only be a limited number of yields (where as in non-blocking 
		mode the command will yield as soon as possible).
		"""
		for seq in self._sendFrame(request):
			if seq == None:
				yield seq

		# Wait for the first packet
		for p in self._recvFrame(seq):
			if p == None:
				yield p

		# The whole command failed :(
		if isinstance(p, objects.Fail):
			yield False, p.s
			return

		# Only one returned value
		elif isinstance(p, type):
			yield [p]
			return

		# Multiple values!
		elif isinstance(p, objects.Sequence):
			yield Progress(of=p.number)

			r = []
			# Get each individual packet
			for i in xrange(0, p.number):
				for p in self.getsingle(seq, type):
					if p == None:
						yield p
				r.append(p)

				yield Progress(number=i, of=p.number)
	
			# Yay got the result!
			yield r

		else:
			# We got a bad packet
			raise IOError("Received a bad packet (was %r)" % p)

	def _getids(self, idseqtype, amount=30):
		"""
		Get the (id, modtime) pairs of a certain type.
		"""
		if not issubclass(idseqtype, objects.GetIDSequence):
			raise TypeError("Given type must be a subclass of 'IDSequence' packet")

		# Send the first request
		for seq in self._sendFrame(idseqtype(-1, -1, 0, amount)):
			if seq == None:
				yield seq

		position = 0
		while True:
			# Wait for the request to come in
			for p in self.getsingle(idseqtype.responses[0]):
				if p == None:
					yield p, None

			position += len(p.ids)

			# Request the next set off IDs
			if p.left > 0:
				self._send(idseqtype(seq, p.key, position, min(amount, p.left)))
			
			# Return each (id, modtime) pair
			for id, modtime in p.ids:
				yield id, modtime

	def disconnect(self):
		"""\
		Disconnect from a server.

		This has no return. This function will either succeed or throw and exception.
		"""
		# FIXME: This should have some way to wait for all the current
		# generators to finish to allow something like this

		# a = Connect()
		# a.connect()
		# a.login()
		# 
		# class Thread(threading.thread):
		#    def run(c):
		#        for id, time in c.get_object_ids(0):
		#            print id, time
		#
		# t = Thread()
		# t.start()
		# # This command blocks until the generator is finished...
		# a.disconnect()
		#
		self.s.close()

	def connect(self, str=""):
		"""\
		Connects to a Thousand Parsec Server.

		(True, "Welcome to ABC") = connect("MyWonderfulClient")
		(False, "To busy atm!")  = connect("MyWonderfulClient")

		You can used the "failed" function to check the result.

		Will transparently handle redirection from the server.
		"""
		# Send a connect packet
		from version import version

		for seq in self._sendFrame(objects.Connect(-1, ("libtpproto-py/%i.%i.%i " % version[:3]) + str)):
			if seq == None:
				yield seq

		for p in self._recvFrame(seq):
			if p == None:
				yield p

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			yield True, p.s
		elif isinstance(p, objects.Fail):
			yield False, p.s

		elif isinstance(p, objects.Redirect):
			# FIXME: Connect to another location...
			self.setup(p.s, debug=self.debug, proxy=self.proxy)

			for y in self.connect():
				yield y
		else:
			# We got a bad packet
			raise IOError("Received a bad packet (was %r)" % p)

	def account(self, username, password, email, comment=""):
		"""\
		Tries to create an account on a Thousand Parsec Server.

		You can used the "failed" function to check the result.
		"""
		return self._okfail(objects.Account(-1, username, password, email, comment))

	def ping(self):
		"""\
		Pings the Thousand Parsec Server.

		(True, "Pong!") = ping()
		(False, "")     = ping()

		You can used the "failed" function to check the result.
		"""
		return self._okfail(objects.Ping(-1))

	def login(self, username, password):
		"""\
		Login to the server using this username/password.

		(True, "Welcome Mithro!")  = login("mithro", "mypassword")
		(False, "Go away looser!") = login("mithro", "mypassword")

		You can used the "failed" function to check the result.
		"""
		return self._okfail(objects.Login(-1, username, password))

	def games(self):
		"""\
		Get all games which are on a server.
		"""
		return self._getmany(objects.Games_Get(-1), objects.Game)

	def features(self):
		"""\
		Gets the features the Thousand Parsec Server supports.

		FIXME: This documentation should be completed.
		"""
		return self._getsingle(objects.Feature_Get(-1), objects.Feature)

	def time(self):
		"""\
		Gets the time till end of turn from a Thousand Parsec Server.

		FIXME: This documentation should be completed.
		"""
		# Send a connect packet
		sequenceno = self._send(objects.TimeRemaining_Get(-1))
		for p in self._recvFrame(seq):
			if p == None:
				yield p

		# Check it's the reply we are after
		if isinstance(p, objects.TimeRemaining):
			# FIXME: This will cause any truth check to fail if p.time is zero!
			yield p.time
		elif isinstance(p, objects.Fail):
			yield False, p.s
		else:
			raise IOError("Received a bad packet (was %r)" % p)

	def get_object_ids(self, a=None, y=None, z=None, r=0, x=None, id=None, iter=False):
		"""\
		Get objects ids from the server,

		# Get all object ids (plus modification times)
		[(25, 10029436), ...] = get_object_ids()

		# Get all object ids (plus modification times) at a location
		[(25, 10029436), ..] = get_objects_ids(x, y, z, radius)
		[(25, 10029436), ..] = get_objects_ids(x=x, y=y, z=z, r=radius)

		# Get all object ids (plus modification times) contain by an object
		[(25, 10029436), ..] = get_objects_ids(id)
		[(25, 10029436), ..] = get_objects_ids(id=id)
		"""
		if a != None and y != None and z != None and r != None:
			x = a
		elif a != None:
			id = a

		if x != None:
			p = objects.Object_GetID_ByPos(-1, x, y, z, r)
		elif id != None:
			p = objects.Object_GetID_ByContainer(-1, id)
		else:
			raise ArgumentError("Must either provide a coordinate or an parent id.")

		for p in self._getsingle(p, objects.Object_IDSequence):
			if p == None:
				yield (None, None)
		
		for id, time in p.ids:
			yield id, time

	def get_objects(self, *args, **kw):
		"""\
		Get objects from the server,

		# Get the object with id=25
		[<obj id=25>] = get_objects(25)
		[<obj id=25>] = get_objects(id=25)
		[<obj id=25>] = get_objects(ids=[25])
		[<obj id=25>] = get_objects([id])

		# Get the objects with ids=25, 36
		[<obj id=25>, <obj id=36>] = get_objects([25, 36])
		[<obj id=25>, <obj id=36>] = get_objects(ids=[25, 36])
		"""
		return self._getmany(objects.Object_GetById(-1, getidsarg(*args, **kw)), objects.Object)

	def get_orders(self, oid, *args, **kw):
		"""\
		Get orders from an object,

		# Get the order in slot 5 from object 2
		[<ord id=2 slot=5>] = get_orders(2, 5)
		[<ord id=2 slot=5>] = get_orders(2, slot=5)
		[<ord id=2 slot=5>] = get_orders(2, slots=[5])
		[<ord id=2 slot=5>] = get_orders(2, [5])

		# Get the orders in slots 5 and 10 from object 2
		[<ord id=2 slot=5>, <ord id=2 slot=10>] = get_orders(2, [5, 10])
		[<ord id=2 slot=5>, <ord id=2 slot=10>] = get_orders(2, slots=[5, 10])

		# Get all the orders from object 2
		[<ord id=2 slot=5>, ...] = get_orders(2)
		"""
		return self._getmany(objects.Order_Get(-1, oid, getslotsarg(*arg, **kw)), objects.Order)

	def insert_order(self, oid, slot, otype, *args, **kw):
		"""\
		Add a new order to an object,

		(True, "Order inserted success")      = insert_order(oid, slot, otype, [arguments for order])
		(False, "Order couldn't be inserted") = insert_order(oid, slot, [Order Object])

		You can used the "failed" function to check the result.
		"""
		o = None
		if isinstance(otype, objects.Order) or isinstance(otype, objects.Order_Insert):
			o = otype
			o.no = objects.Order_Insert.no
			o._type = objects.Order_Insert.no

			o.id = oid
			o.slot = slot

			o.sequence = -1
		else:
			o = objects.Order_Insert(-1, oid, slot, otype, 0, [], *args)

		return self._okfail(o)

	def remove_orders(self, oid, *args, **kw):
		"""\
		Removes orders from an object,

		# Remove the order in slot 5 from object 2
		[<Ok>] = remove_orders(2, 5)
		[<Ok>] = remove_orders(2, slot=5)
		[<Ok>] = remove_orders(2, slots=[5])
		[(False, "No order 5")] = remove_orders(2, [5])

		# Remove the orders in slots 5 and 10 from object 2
		[<Ok>, (False, "No order 10")] = remove_orders(2, [5, 10])
		[<Ok>, (False, "No order 10")] = remove_orders(2, slots=[5, 10])
		"""
		return self._getmany(objects.Order_Remove(-1, oid, getslotsarg(*arg, **kw)), objects.Ok)

	def get_orderdesc_ids(self):
		"""\
		Get orderdesc ids from the server,

		# Get all order description ids (plus modification times)
		[(25, 10029436), ...] = get_orderdesc_ids()
		"""
		return self._getids(objects.OrderDesc_IDSequence)

	def get_orderdescs(self, *args, **kw):
		"""\
		Get order descriptions from the server. 

		Note: When the connection gets an order which hasn't yet been
		described it will automatically get an order description for that
		order, you don't need to do this manually.

		# Get the order description for id 5
		[<orddesc id=5>] = get_orderdescs(5)
		[<orddesc id=5>] = get_orderdescs(id=5)
		[<orddesc id=5>] = get_orderdescs(ids=[5])
		[(False, "No desc 5")] = get_orderdescs([5])

		# Get the order description for id 5 and 10
		[<orddesc id=5>, (False, "No desc 10")] = get_orderdescs([5, 10])
		[<orddesc id=5>, (False, "No desc 10")] = get_orderdescs(ids=[5, 10])
		"""
		return self._getmany(objects.OrderDesc_Get(-1, getidsarg(*args, **kw)), objects.OrderDesc)

	def get_board_ids(self, iter=False):
		"""\
		Get board ids from the server,

		# Get all board ids (plus modification times)
		[(25, 10029436), ...] = get_board_ids()
		"""
		return self._getids(objects.Board_IDSequence)

	def get_boards(self, x=None, id=None, ids=None):
		"""\
		Get boards from the server,

		# Get the board with id=25
		[<board id=25>] = get_boards(25)
		[<board id=25>] = get_boards(id=25)
		[<board id=25>] = get_boards(ids=[25])
		[(False, "No such board")] = get_boards([id])

		# Get the boards with ids=25, 36
		[<board id=25>, (False, "No board")] = get_boards([25, 36])
		[<board id=25>, (False, "No board")] = get_boards(ids=[25, 36])
		"""
		return self._getmany(objects.OrderDesc_Get(-1, getidsarg(*args, **kw)), object.Board)

	def get_messages(self, bid, *args, **kw):
		"""\
		Get messages from an board,

		# Get the message in slot 5 from board 2
		[<msg id=2 slot=5>] = get_messages(2, 5)
		[<msg id=2 slot=5>] = get_messages(2, slot=5)
		[<msg id=2 slot=5>] = get_messages(2, slots=[5])
		[(False, "No such 5")] = get_messages(2, [5])

		# Get the messages in slots 5 and 10 from board 2
		[<msg id=2 slot=5>, (False, "No such 10")] = get_messages(2, [5, 10])
		[<msg id=2 slot=5>, (False, "No such 10")] = get_messages(2, slots=[5, 10])
		"""
		return self._getmany(objects.Message_Get(-1, bid, getslotsarg(*args, **kw)), objects.Message)

	def insert_message(self, bid, slot, message, *args, **kw):
		"""\
		Add a new message to an board.

		Forms are
		[<Ok>] = insert_message(bid, slot, [arguments for message])
		[(False, "Insert failed")] = insert_message(bid, slot, [Message Object])
		"""
		o = None
		if isinstance(message, objects.Message) or isinstance(message, objects.Message_Insert):
			o = message
			o._type = objects.Message_Insert.no
			o.sequence = -1
		else:
			o = objects.Message_Insert(-1, bid, slot, message, *args, **kw)

		return self._okfail(o)

	def remove_messages(self, oid, *args, **kw):
		"""\
		Removes messages from an board,

		# Remove the message in slot 5 from board 2
		[<Ok>] = remove_messages(2, 5)
		[<Ok>] = remove_messages(2, slot=5)
		[<Ok>] = remove_messages(2, slots=[5])
		[(False, "Insert failed")] = remove_messages(2, [5])

		# Remove the messages in slots 5 and 10 from board 2
		[<Ok>, (False, "No such 10")] = remove_messages(2, [10, 5])
		[<Ok>, (False, "No such 10")] = remove_messages(2, slots=[10, 5])
		"""
		return self._getmany(objects.Message_Remove(-1, bid, getslotsarg(*args, **kw)), objects.Ok)

	def get_resource_ids(self, iter=False):
		"""\
		Get resource ids from the server,

		# Get all resource ids (plus modification times)
		[(25, 10029436), ...] = get_resource_ids()

		# Get all object ids (plus modification times) via an Iterator
		<Iter> = get_resource_ids(iter=True)
		"""
		return self._getids(objects.Resource_GetID)

	def get_resources(self, *arg, **kw):
		"""\
		Get resources from the server,

		# Get the resources with id=25
		[<board id=25>] = get_resources(25)
		[<board id=25>] = get_resources(id=25)
		[<board id=25>] = get_resources(ids=[25])
		[(False, "No such board")] = get_resources([id])

		# Get the resources with ids=25, 36
		[<board id=25>, (False, "No board")] = get_resources([25, 36])
		[<board id=25>, (False, "No board")] = get_resources(ids=[25, 36])
		"""
		return self._getmany(objects.Resource_Get(-1, getidsarg(*arg, **kw)), object.Resource)

	def get_category_ids(self, iter=False):
		"""\
		Get category ids from the server,

		# Get all category ids (plus modification times)
		[(25, 10029436), ...] = get_category_ids()
		"""
		return self._getids(objects.Category_GetID)

	def get_categories(self, *args, **kw):
		"""\
		Get category information,

		# Get the information for category 5
		[<cat id=5>] = get_categories(5)
		[<cat id=5>] = get_categories(id=5)
		[<cat id=5>] = get_categories(ids=[5])
		[(False, "No such 5")] = get_categories([5])

		# Get the information for category 5 and 10
		[<cat id=5>, (False, "No such 10")] = get_categories([5, 10])
		[<cat id=5>, (False, "No such 10")] = get_categories(ids=[5, 10])
		"""
		return self._getmany(objects.Category_Get(-1, getidsarg(*arg, **kw)), object.Category)

	def insert_category(self, *args, **kw):
		"""\
		Add a new category.

		<category> = insert_category(id, [arguments for category])
		<Fail> = insert_category([Category Object])
		"""
		d = None
		if isinstance(args[0], objects.Category) or isinstance(args[0], objects.Category_Add):
			d = args[0]
			d.no = objects.Category_Add.no
			d._type = objects.Category_Add.no

			d.sequence = -1
		else:
			d = objects.Category_Add(-1, *args, **kw)

		return self._okfail(d)

	def remove_categories(self, a=None, id=None, ids=None):
		"""\
		Remove categories from the server,

		# Get the category with id=25
		[<ok>] = remove_categories(25)
		[<ok>] = remove_categories(id=25)
		[<ok>] = remove_categories(ids=[25])
		[<ok>] = remove_categories([id])

		# Get the categories with ids=25, 36
		[<ok>, <ok>] = remove_categories([25, 36])
		[<ok>, <ok>] = remove_categories(ids=[25, 36])
		"""
		if a != None:
			if hasattr(a, '__getitem__'):
				ids = a
			else:
				id = a

		if id != None:
			ids = [id]

		return self._getmany(objects.Category_Remove(-1, ids), objects.Ok)

	def get_design_ids(self, iter=False):
		"""\
		Get design ids from the server,

		# Get all design ids (plus modification times)
		[(25, 10029436), ...] = get_design_ids()
		"""
		return self._getids(objects.Design_GetID)

	def get_designs(self, *args, **kw):
		"""\
		Get designs descriptions,

		# Get the information for design 5
		[<des id=5>] = get_designs(5)
		[<des id=5>] = get_designs(id=5)
		[<des id=5>] = get_designs(ids=[5])
		[(False, "No such 5")] = get_designs([5])

		# Get the information for design 5 and 10
		[<des id=5>, (False, "No such 10")] = get_designs([5, 10])
		[<des id=5>, (False, "No such 10")] = get_designs(ids=[5, 10])
		"""
		return self._getmany(objects.Design_Get(-1, getidsarg(*arg, **kw)), object.Design)

	def insert_design(self, *args, **kw):
		"""\
		Add a new design.

		<design> = insert_design(id, [arguments for design])
		<Fail> = insert_design([Design Object])
		"""
		d = None
		if isinstance(args[0], objects.Design) or isinstance(args[0], objects.Design_Add):
			d = args[0]
			d.no = objects.Design_Add.no
			d._type = objects.Design_Add.no

			d.sequence = -1
		else:
			d = objects.Design_Add(-1, *args, **kw)

		return self._getsingle(d, objects.Design)

	def change_design(self, *args, **kw):
		"""\
		Change a new design.

		<design> = change_design(id, [arguments for design])
		<Fail> = change_design([Design Object])
		"""
		d = None
		if isinstance(args[0], objects.Design) or isinstance(args[0], objects.Design_Change):
			d = args[0]
			d.no = objects.Design_Change.no
			d._type = objects.Design_Change.no

			d.sequence = -1
		else:
			d = objects.Design_Change(-1, *args, **kw)

		return self._getsingle(d, objects.Design)

	def remove_designs(self, a=None, id=None, ids=None):
		"""\
		Remove designs from the server,

		# Get the design with id=25
		[<ok>] = remove_designs(25)
		[<ok>] = remove_designs(id=25)
		[<ok>] = remove_designs(ids=[25])
		[<ok>] = remove_designs([id])

		# Get the designs with ids=25, 36
		[<ok>, <ok>] = remove_designs([25, 36])
		[<ok>, <ok>] = remove_designs(ids=[25, 36])
		"""
		if a != None:
			if hasattr(a, '__getitem__'):
				ids = a
			else:
				id = a

		if id != None:
			ids = [id]

		return self._getmany(objects.Design_Remove(-1, ids), objects.Ok)

	def get_component_ids(self, iter=False):
		"""\
		Get component ids from the server,

		# Get all component ids (plus modification times)
		[(25, 10029436), ...] = get_component_ids()
		"""
		return self._getids(objects.Component_GetID)

	def get_components(self, *args, **kw):
		"""\
		Get components descriptions,

		# Get the description for components 5
		[<com id=5>] = get_components(5)
		[<com id=5>] = get_components(id=5)
		[<com id=5>] = get_components(ids=[5])
		[(False, "No such 5")] = get_components([5])

		# Get the descriptions for components 5 and 10
		[<com id=5>, (False, "No such 10")] = get_components([5, 10])
		[<com id=5>, (False, "No such 10")] = get_components(ids=[5, 10])
		"""
		return self._getmany(objects.Component_Get(-1, getidsarg(*arg, **kw)), object.Component)

	def get_property_ids(self, iter=False):
		"""\
		Get property ids from the server,

		# Get all property ids (plus modification times)
		[(25, 10029436), ...] = get_property_ids()
		"""
		return self._getids(objects.Property_GetID)

	def get_properties(self, *args, **kw):
		"""\
		Get properties descriptions,

		# Get the description for properties 5
		[<pro id=5>] = get_properties(5)
		[<pro id=5>] = get_properties(id=5)
		[<pro id=5>] = get_properties(ids=[5])
		[(False, "No such 5")] = get_properties([5])

		# Get the descriptions for properties 5 and 10
		[<pro id=5>, (False, "No such 10")] = get_properties([5, 10])
		[<pro id=5>, (False, "No such 10")] = get_properties(ids=[5, 10])
		"""
		return self._getmany(objects.Property_Get(-1, getidsarg(*arg, **kw)), object.Property)

	def get_players(self, *args, **kw):
		"""\
		Get players descriptions,

		# Get the description for players 5
		[<pro id=5>] = get_players(5)
		[<pro id=5>] = get_players(id=5)
		[<pro id=5>] = get_players(ids=[5])
		[(False, "No such 5")] = get_players([5])

		# Get the descriptions for players 5 and 10
		[<pro id=5>, (False, "No such 10")] = get_players([5, 10])
		[<pro id=5>, (False, "No such 10")] = get_players(ids=[5, 10])
		"""
		return self._getmany(objects.Player_Get(-1, getidsarg(*arg, **kw)), object.Player)

