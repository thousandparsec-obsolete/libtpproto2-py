

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

class Connection(object):
	pass



class ClientConnection(Connection):
	def okfail(self, seq):
		"""
		Deal with a Okay or Fail return.
		"""
		for p in self._recvg(seq):
			if p == None:
				yield
			break

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			return True, p.s
		elif isinstance(p, objects.Fail):
			return False, p.s

		# We got a bad packet
		raise IOError("Received a bad packet (was %r)" % p)

	def getsingle(self, seq, type):
		"""
		Deal with a Fail or give packet type return.
		"""
		for p in self._recvg(seq):
			if p == None:
				yield
			break

		if isinstance(p, type):
			yield p
		elif isinstance(p, objects.Fail):
			yield False, p.s

		# We got a bad packet
		else:
			raise IOError("Received a bad packet (was %r)" % p)

	def getmany(self, seq, type):
		"""\
		Deal with a Sequence of a given packet type return.

		It will,
			yield None,     if no information
			yield Progress, if some progress has been made (Progress instances == None)
			yield tuple,    if the get failed for a reason
			yield list,     if the get returned some information

		Simple way to do this in "blocking" mode:
			for result in connection.getmany(12, <type>):
				if result != None:
					break
			if failed(result):
				print "The command failed :/", result[1]
			print "The command worked!", r

		You don't need a sleep in the for loop because the socket is blocking and 
		hence there will only be a limited number of yields (where as in non-blocking 
		mode the command will yield as soon as possible).
		"""
		# Wait for the first packet
		for p in self._recvg(seq):
			if p == None:
				yield
			break

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
						yield
					break
				r.append(p)

				yield Progress(number=i, of=p.number)
	
			# Yay got the result!
			yield r

		else:
			# We got a bad packet
			raise IOError("Received a bad packet (was %r)" % p)

	def getids(self, sequence, idseqtype, amount=30):
		"""
		Get the (id, modtime) pairs of a certain type.
		"""
		if not issubclass(idseqtype, objects.GetIDSequence):
			raise TypeError("Given type must be a subclass of 'IDSequence' packet")

		# Send the first request
		self._send(idseqtype(sequence, -1, 0, amount)):

		position = 0
		while True:
			# Wait for the request to come in
			for p in self.getsingle(idseqtype.responses[0]):
				if p == None:
					yield None, None
				break

			position += len(p.ids)

			# Request the next set off IDs
			if p.left > 0:
				self._send(idseqtype(sequence, p.key, position, min(amount, p.left)))
			
			# Return each (id, modtime) pair
			for id, modtime in p.ids:
				yield id, modtime

	def account(self, username, password, email, comment=""):
		"""\
		Tries to create an account on a Thousand Parsec Server.

		You can used the "failed" function to check the result.
		"""
		self.sequence += 1

		self._send(objects.Account(self.sequence, username, password, email, comment)):
		return self.okfail(self.sequence)


