
# Python imports
import socket
import select
import time
import sys

# Local imports
import xstruct
import objects

def red(*args):
	print args
def green(*args):
	print args

try:
	set()
except NameError:
	from sets import Set as set

class NotImplimented(Exception):
	pass

class SSLWrapper(object):
	def __init__(self, s):
		self.base = s

		try:
			import OpenSSL.crypto
			import OpenSSL.SSL as SSL

			context = SSL.Context(SSL.SSLv23_METHOD)
			context.set_verify(SSL.VERIFY_NONE, lambda a, b, c, d, e: True)

			self.s = SSL.Connection(context, s)
			self.s.set_connect_state()
			self.socket_error = (SSL.WantReadError, SSL.WantWriteError,)

			print "Found pyopenssl"
			return
		except ImportError, e:
			print "Unable to import pyopenssl"

		try:
			from tlslite.api import TLSConnection

			class tlslite_wrapper(object):
				def __init__(self, s):
					self.s = TLSConnection(s)
					self.s.handshakeClientCert()

					self.writing = None
					self.reading = None

				def write(self, data):
					if self.writing is None:
						self.writing = (len(data), self.s.writeAsync(data))

					try:
						self.writing[1].next()
						return 0
					except StopIteration:
						pass

					sent = self.writing[0]
					self.writing = None
					return sent

				def read(self, amount):
					d = None
					while d == None:
						try:
							d = self.reading.next()
						except (StopIteration, AttributeError):
							self.reading = self.s.readAsync(amount)

					try:
						len(d)
					except:
						raise socket.error("No data ready to be read.")
					return d

			self.s = tlslite_wrapper(s)
			self.socket_error = tuple()
			return
		except ImportError, e:
			print "Unable to import tlslite"

		try:
			self.s = socket.ssl(s)
			self.socket_error = (IOError,)
			print "Using crappy inbuilt SSL connection, be warned there can be no verification."
		except ValueError, e:
			raise IOError("Unable to find a working SSL library." + e)

	def send(self, data):
		no = 0
		while no != len(data):
			try:
				no += self.s.write(data)
			except self.socket_error, e:
				print "SSL send", e.__class__, e
		return no

	def recv(self, amount):
		try:
			data = self.s.read(amount)
			return data
		except self.socket_error, e:
			print "SSL recv", e.__class__, e

	def setblocking(self, t):
		self.base.setblocking(t)

import os
from threading import Lock
class StringQueue(object):
	def __init__(self):
		self.reader, self.writer = os.pipe()
		self.readbytes = self.wrotebytes = 0

		self.readlock  = Lock()
		self.writelock = Lock()

	def left(self):
		return int(self.wrotebytes - self.readbytes)
	__len__ = left

	def read(self, amount):
		self.readbytes += amount
		return os.read(self.reader, amount)

	def write(self, string):
		self.wrotebytes += len(string)
		os.write(self.writer, string)

	def __str__(self):
		return "<StringQueue left(%i)>" % self.left()
	__repr__ = __str__

class LockableDict(dict):
	__slots__ = ['lock']

	def __init__(self, *args, **kw):
		dict.__init__(self, *args, **kw)
		self.lock = Lock()

class LockableList(list):
	__slots__ = ['lock']

	def __init__(self, *args, **kw):
		list.__init__(self, *args, **kw)
		self.lock = Lock()

class ConnectionCommon(object):
	"""\
	Base class for Thousand Parsec protocol connections.
	Methods common to both server and client connections
	go here.
	"""
	def __init__(self):
		self.__recvFrames = self.__recvFramesGenerator()

		self.debug = False

		self.frames = LockableDict()
		self.frames['sent'] = 0
		self.frames['recv'] = 0

		self.buffered = {}
		self.buffered['frames-received'] = LockableDict()
		self.buffered['bytes-received']  = StringQueue()
		self.buffered['bytes-tosend']    = StringQueue()

	def __recvBytes(self):
		"""
		** WARNING ** - Not thread safe.

		Called to recv bytes
		"""
		pass

	def __sendBytes(self):
		"""
		** WARNING ** - Not thread safe.

		Called to send bytes...
		"""
		pass

	def _sendFrame(self, packet):
		"""\
		Write a single TP packet to the socket.
		"""
		frames = self.frames

		if not isinstance(packet, objects.Header):
			raise TypeError('Can only send Thousand Parsec Frames! Not %r' % packet)

		# Get lock
		while not frames.lock.acquire(False):
			yield

		# Increase the frame counter
		self.frames['sent'] += 1

		if packet.sequence == -1:
			# Set the sequence on this out going frame
			packet.sequence = frames['sent']

		# Put the bytes into the outgoing queue
		bytes = self.buffered['bytes-tosend']
		while not bytes.writelock.acquire(False):
			yield
		bytes.write(str(packet))
		bytes.writelock.release()

		# Release lock
		frames.lock.release()

		# Return the sequence
		yield packet.sequence

	def __recvFramesGenerator(self):
		"""
		You must have a lock on 'frames-received' before calling this fuction.
		"""
		# FIXME: This is bad! It will block other "threads" until this generator is called...
		while True:
			bytes = self.buffered['bytes-received']
		
			# Get the header
			size = objects.Header.size
			while True:
				# We need to hold a lock on receive queue until we have the whole packet
				if len(bytes) >= size and bytes.readlock.acquire(False):
					break
				yield

			packet = objects.Header.fromstr(bytes.read(size)) 

			# Get the body
			while True:
				if len(self.buffered['bytes-received']) >= packet.length:
					break
				yield
			packet._data = self.buffered['bytes-received'].read(packet.length)

			# Release the lock
			bytes.readlock.release()

			# Put the frame into the frames-received
			frames = self.buffered['frames-received']
			if not frames.has_key(packet.sequence):
				frames[packet.sequence] = []
			frames[packet.sequence].append(packet)

	def _recvFrame(self, sequence):
		"""
		Gets a frame with a specific ID..
		"""
		frames = self.buffered['frames-received']

		while True:
			# Need to lock the frames before we can manipulate them
			while not frames.lock.acquire(False):
				yield

			# See if a packet is sequence..
			if not frames.has_key(sequence):
				# Process any incoming frames
				self.__recvFrames.next()

				# Release the lock...
				frames.lock.release()

				yield
				continue

			p = frames[sequence][0]
			# Try to process the frame
			if hasattr(p, '_data'):
				try:
					p.__process__(p._data)
					del p._data

					# Tell everyone we have recieved the packet
					if self.debug:
						red("Receiving: %r\n" % p)

				except objects.DescriptionError:
					# Need to release the lock as _description_error might request
					# frames!
					frames.lock.release()
					self._description_error(p)
					continue

			# Clean up the frames
			del frames[sequence][0]
			if len(frames[sequence]) == 0:
				del frames[sequence]

			frames.lock.release()
			yield p
			break

	def _description_error(self, packet):
		"""\
		Called when we get a packet which hasn't be described.

		The packet will be of type Header ready to be morphed by calling
		process as follows,

		p.process(p._data)
		"""
		raise objects.DescriptionError("Can not deal with an undescribed packet.")

	def _version_error(self, h):
		"""\
		Called when a packet of the wrong version is found.

		The function should either raise the error or return a
		packet with the correct version.
		"""
		raise

BUFFER_SIZE = 1024

class Connection(ConnectionCommon):
	"""\
	Base class for Thousand Parsec protocol connections.
	Methods common to both server and client connections
	go here.
	"""
	def __init__(self):
		ConnectionCommon.__init__(self)

	def setup(self, s, debug=False):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		self.s = s
		self.s.setblocking(False)

		self.debug = debug

	def __recvBytes(self):
		"""\
		Receive a bunch of bytes onto the socket.
		"""
		buffer = self.buffered['bytes-received']
		try:
			data = self.s.recv(BUFFER_SIZE)
			if data == '':
				raise IOError("Socket.recv returned no data, connection must have been closed...")

			if self.debug and len(data) > 0:
				red("Received: %s \n" % xstruct.hexbyte(data))

			buffer.write(data)
		except socket.error, e:
			pass

	def __sendBytes(self):
		"""\
		Send a bunch of bytes onto the socket.
		"""
		buffer = self.buffered['bytes-tosend']

		sent = 0
		try:
			if len(buffer) > 0:
				sent = self.s.send(buffer.read(len(buffer)))
		except socket.error, e:
			if self.debug:
				print "Send Socket Error", e

		if self.debug and sent > 0:
			green("Sending: %s \n" % xstruct.hexbyte(buffer.peek(sent)))

	def fileno(self):
		"""\
		Returns the file descriptor number.
		"""
		# This is cached so our fileno doesn't go away when the socket dies..
		if not hasattr(self, "_fileno"):
			self._fileno = self.s.fileno()
		return self._fileno

	def pump(self):
		"""\
		Causes the connection to read and process stuff from the
		buffer. This will allow you to read out of band messages.

		Calling oob will also cause the connection to be pumped.
		"""
		if not hasattr(self, 's'):
			return

		self.__sendBytes()
		self.__recvBytes()

