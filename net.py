from twisted.internet import reactor, protocol, task
from twisted.spread import pb
import pyglet
from model import *

PORT = 4444

class GGJServer(pb.Root):
	def __init__(self):
		pass

	def remote_login(self, name):
		print "New client connected"
#		return (1, world.state())
		return 1

class GGJClient:
	def __init__(self, host):
		print "Connecting to server:", host
		factory = pb.PBClientFactory()
		reactor.connectTCP(host, PORT, factory)
		factory.getRootObject().addCallbacks(self.connected, self.failure)

	def connected(self, perspective):
		self.perspective = perspective
		print "Connected! Wahoo!"
		perspective.callRemote('login', "winnerer")
	
	def failure(self, failure):
		print "Boo failure connecting to server!"

def server_world():
	"""This runs the protocol on port 4444"""
	world = local_world()

	factory = pb.PBServerFactory(GGJServer())
	reactor.listenTCP(PORT, factory)

	return world


def client_world(remote_host):
	GGJClient(remote_host)
	return World()

def local_world():
	world = World()
	
	for i in xrange(16):
		world.buildings.append(Building(i))
	
	for i in xrange(1):
		world.add_dude()

	return world

def server_update():
	dt = pyglet.clock.tick(poll=False)
	world.update(dt)

# this only runs if the module was *not* imported
if __name__ == '__main__':
	start_server()
	update = task.LoopingCall(server_update)
	update.start(1/60.)
	reactor.run()
