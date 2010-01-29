from twisted.internet import reactor, protocol, task
import pyglet
from model import *

class GGJServer(protocol.Protocol):
	def dataReceived(self, data):
		self.transport.write(data)
	
	def connectionMade(self):
		self.transport.write("o hi")

def start_server():
	"""This runs the protocol on port 4444"""
	factory = protocol.ServerFactory()
	factory.protocol = GGJServer
	reactor.listenTCP(4444, factory)

def server_update():
	dt = pyglet.clock.tick(poll=False)
	world.update(dt)

# this only runs if the module was *not* imported
if __name__ == '__main__':
	start_server()
	update = task.LoopingCall(server_update)
	update.start(1/60.)
	reactor.run()
