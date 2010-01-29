from twisted.internet import reactor, protocol, task
import pyglet
from model import *

class GGJServer(protocol.Protocol):
	def dataReceived(self, data):
		self.transport.write(data)
	
	def connectionMade(self):
		self.transport.write("o hi")

def server_world():
	"""This runs the protocol on port 4444"""
	factory = protocol.ServerFactory()
	factory.protocol = GGJServer
	reactor.listenTCP(4444, factory)
	world = local_world()

	return world


def client_world(remote_host):
	return World()

def local_world():
	world = World()
	
	for i in xrange(16):
		world.buildings.append(Building(i))
	
	for i in xrange(20):
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
