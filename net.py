from twisted.internet import reactor, protocol, task
from twisted.spread import pb
from model import World
import pyglet

PORT = 4444

is_server = False
peers = []

def broadcast_dude_update(state):
	print "broadcast"
	id = state[0]
	for peer in peers:
		if not is_server or peer.dude_id != id:
			peer.callRemote('local_dude_state', state)

class GGJPeer(pb.Root):
	def __init__(self, world=None, host=None):
		global is_server
		
		if world != None:
			self.world = world
			self.unused_player_ids = range(1, len(self.world.dudes))
			is_server = True
		elif host != None:
			print "Connecting to server:", host
			factory = pb.PBClientFactory()
			reactor.connectTCP(host, PORT, factory)
			d = factory.getRootObject().addCallbacks(self.connected, self.failure)
			d.addCallbacks(self.got_world_state, self.failure)
			self.deferred = d
			is_server = False
		else:
			raise Exception("invalid peer - must be a server or a client")

	def remote_local_dude_state(self, dude_state):
		self.world.update_dude(dude_state)
		
		if is_server:
			broadcast_dude_update(dude_state)
			print "server broadcast"

# Server function. Client calls this when it connects
	def remote_login(self, name, peer):
		print "New client connected with name", name
		peers.append(peer)
		if len(self.unused_player_ids) == 0: return None # no player IDs left!
		peer.dude_id = self.unused_player_ids.pop(0)
		return (peer.dude_id, self.world.state())

# called on client - client has connected
	def connected(self, perspective):
		print "Connected! Wahoo!"
		peers.append(perspective)
		return perspective.callRemote('login', "winnerer", self)

	def got_world_state(self, result):
		print "got world state"
		(self.dude_id, state) = result
		self.world = World(state=state)
		return self.world
	
	def failure(self, failure):
		print "Boo failure connecting to server!"

def server_world():
	"""This runs the protocol on port 4444"""
	world = World()

	factory = pb.PBServerFactory(GGJPeer(world=world))
	reactor.listenTCP(PORT, factory)

	return world


def client_world(remote_host):
	client = GGJPeer(host=remote_host)
	return client.deferred

def server_update():
	dt = pyglet.clock.tick(poll=False)
	world.update(dt)

# this only runs if the module was *not* imported
if __name__ == '__main__':
	start_server()
	update = task.LoopingCall(server_update)
	update.start(1/60.)
	reactor.run()



