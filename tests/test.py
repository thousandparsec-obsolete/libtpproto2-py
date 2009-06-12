"""FIXME: This test does not work.

import tp.netlib.client

import socket, time, sys, random

c = tp.netlib.client.ClientConnection()
c.setup('localhost')

a = c.connect()
print a
for t in a:
	if t is None:
		c.pump()
	else:
		print repr(t)


a = c.login('testing', 'test')
print a
for t in a:
	if t is None:
		c.pump()
	else:
		print repr(t)

sys.stdout.flush()

import threading
class a(threading.Thread):
	def __init__(self, c):
		threading.Thread.__init__(self)
		self.c = c

	def run(self):
		l = []
		for t in self.c.get_object_ids():
			print self, t
			sys.stdout.flush()

			if t == (None, None):
				c.pump()
			else:
				l.append(t[0])
			time.sleep(random.randint(0,5))

		time.sleep(random.randint(0,5))

		print self, l
		sys.stdout.flush()

		for t in self.c.get_objects(l):
			print self, repr(t)
			sys.stdout.flush()

			if t == None:
				c.pump()

			time.sleep(random.randint(0,5))

class b(threading.Thread):
	def __init__(self, c):
		threading.Thread.__init__(self)
		self.c = c

	def run(self):
		l = []
		for t in self.c.get_resource_ids():
			print self, t
			sys.stdout.flush()

			if t == (None, None):
				c.pump()
			else:
				l.append(t[0])
			time.sleep(random.randint(0,15))

		time.sleep(random.randint(0,15))
		print self, l
		sys.stdout.flush()

		for t in self.c.get_resources(l):
			print self, repr(t)
			sys.stdout.flush()

			if t == None:
				c.pump()

			time.sleep(random.randint(0,15))
a = a(c)
b = b(c)

b.start()
a.start()
"""