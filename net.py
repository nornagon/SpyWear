from twisted.internet import reactor, protocol, task
from twisted.spread import pb
from model import World
import pyglet

PORT = 4444

peers = []

def broadcast_state(state, function, suppressId = None):
	for peer in peers:
		if not (World.is_server and suppressId != None and peer.dude_id == suppressId):
			peer.callRemote(function, state)

def broadcast_dude_update(state):
	id = state[0]
	broadcast_state(state, 'local_dude_state', suppressId = id)

def broadcast_building_explosion(state):
	terrorist_id, building_id = state
	broadcast_state(state, 'explode', suppressId = terrorist_id)

def broadcast_die(murderer, victim):
	broadcast_state((murderer, victim), 'die', suppressId=murderer)

def broadcast_player_update(state):
	id = state[0]
	broadcast_state(state, 'player_state')#, suppressId = id)

# only ever called from the server
def broadcast_player_dropped(player_dropped_id):
	broadcast_state(player_dropped_id, 'player_dropped')

def broadcast_hint(playerID, attr):
	for peer in peers:
		peer.callRemote('hint', playerID, attr)

	if attr == 'appearance':
		print 'got appearance hint for',playerID
		World.get_world().players[playerID].reveal_appearance = 5
	elif attr == 'mission':
		print 'got mission hint for',playerID
		World.get_world().players[playerID].reveal_mission = 5

class GGJPeer(pb.Root):
	def __init__(self, world=None, host=None):
		if world != None:
			self.world = world
			World.is_server = True
		elif host != None:
			print "Connecting to server:", host
			factory = pb.PBClientFactory()
			reactor.connectTCP(host, PORT, factory)
			d = factory.getRootObject().addCallbacks(self.connected, self.failure)
			self.deferred = d
			World.is_server = False
		else:
			raise Exception("invalid peer - must be a server or a client")

	def remote_local_dude_state(self, dude_state):
		self.world.update_dude(dude_state)
		
		if World.is_server:
			broadcast_dude_update(dude_state)

	def remote_explode(self, state):
		self.world.remote_explode(state)
		
		if World.is_server:
			broadcast_building_explosion(state)

	def remote_die(self, state):
		(murderer, victim) = state
		self.world.dudes[victim].die()
		if World.is_server:
			broadcast_die(murderer, victim)

	def remote_hint(self, playerID, attr):
		if attr == 'appearance':
			print 'got appearance hint for',playerID
			World.get_world().players[playerID].reveal_appearance = 5
		elif attr == 'mission':
			print 'got mission hint for',playerID
			World.get_world().players[playerID].reveal_mission = 5

	def remote_player_state(self, state):
		self.world.set_player_state(state)
		if World.is_server:
			broadcast_player_update(state)

	def remote_player_dropped(self, player_dropped_id):
		self.world.drop_player(player_dropped_id)

# Server function. Client calls this when it connects
	def remote_login(self, name, peer):
		print "New client connected with name", name

		peer.dude_id = self.world.allocate_new_playerid(suppressUpdate = True)
		if peer.dude_id is None:
			raise "Too many players!"
		peers.append(peer)
		peer.notifyOnDisconnect(self.onClientDropped)
		print "new peer id allocated:", peer.dude_id
		print [p.dude_id for p in peers]

		return (peer.dude_id, self.world.state())

# called on client - client has connected
	def connected(self, perspective):
		print "Connected! Wahoo!"
		peers.append(perspective)
		perspective.notifyOnDisconnect(self.onServerDropped)
		return perspective.callRemote('login', "winnerer",
				self).addCallbacks(self.got_world_state, self.failure)

	def got_world_state(self, result):
		print "got world state"
		(self.dude_id, state) = result
		self.world = World(state=state)
		return (self.dude_id, self.world)
	
	def failure(self, failure):
		print "Boo failure connecting to server!"
		reactor.stop()
		return failure

	def onClientDropped(self, peer):
		print "something disconnected", peer
		peers.remove(peer)
		World.get_world().drop_player(World.get_world().dudes[peer.dude_id].player_id)

	def onServerDropped(self, peer):
		if World.get_world():
			World.get_world().connected = False

def server_world():
	"""This runs the protocol on port 4444"""
	world = World()

	factory = pb.PBServerFactory(GGJPeer(world=world))
	reactor.listenTCP(PORT, factory)

	return (0, world)


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



