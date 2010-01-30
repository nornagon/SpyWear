import random
from pyglet import *
import math

world = None

COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)

class World:
	def __init__(self, state = None):
		self.buildings = []
		self.dudes = []
		self.dudes_batch = graphics.Batch()
		self.background = image.load('assets/City.png')
		self.hud_mockup = image.load('assets/hud_mockup.png')
		self.doors = []

		if state is None:
			# init
			for i in xrange(16):
				building = Building(i)
				self.buildings.append(building)
				self.add_door(building)

			for i in xrange(20):
				self.add_dude()
		else:
			# construct from given state
			(building_state, dude_state) = state

			for i in xrange(len(building_state)):
				building = Building(i, building_state[i])
				self.buildings.append(building)
				self.add_door(building)

			self.dudes = [Dude(batch=self.dudes_batch, state=s) for s in dude_state]

	__instance = None
	@classmethod
	def get_world(cls):
		return cls.__instance

	@classmethod
	def set_world(cls, world):
		cls.__instance = world


	def add_dude(self):
		d = Dude(id = len(self.dudes), batch = self.dudes_batch)
		d.randomise()
		self.dudes.append(d)

	def add_door(self, building):
		# building ID determines location
		x = (28 + 202 * (building.id % 4))/768.
		y = (28 + 202 * (building.id / 4))/768.
		# door ID determines path and location float
		doorx, doory = building.BUILDING_TYPE[building.type][1]
		if doorx == 0:
			# left path
			path = (building.id % 4) * 2 + 8
			door_location = y + doory
			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location

		if doorx == 1:
			# right path
			path = (building.id % 4) * 2 + 9
			door_location = y + doory
			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location

		if doory == 0:
			# lower path
			path = (building.id / 4) * 2
			door_location = x + doorx
			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location

		if doory == 1:
			# upper path
			path = (building.id / 4) * 2 + 1
			door_location = x + doorx
			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location
                
	def get_player(self, myplayerID):
		return self.dudes[myplayerID]

	def draw(self, window):
		window.clear()

		# background
		self.background.blit(256,0)
		self.hud_mockup.blit(0,0)

		for d in self.dudes:
			d.draw(window)
		self.dudes_batch.draw()

		for b in self.buildings:
			b.draw(window)

		# hud
		label = text.Label("FPS: %d" % clock.get_fps(), font_name="Georgia",
				font_size=24, x=0, y=7)
		label.draw()

	def update(self, time):
		for b in self.buildings:
			b.update(time)

		for d in self.dudes:
			d.update(time)

	# For net sync
	def state(self):
		return ([b.state() for b in self.buildings], [d.state() for d in self.dudes])

	def update_dude(self, dude_state):
		self.dudes[dude_state[0]].update_local_state(dude_state)

class Building:
	TYPE_CLOTHES, TYPE_BOMB, TYPE_HOSPITAL, TYPE_MUSEUM,\
	TYPE_DISCO, TYPE_ARCADE, TYPE_CARPARK, TYPE_FACTORY,\
	TYPE_OFFICE, TYPE_PARK, TYPE_WAREHOUSE, TYPE_BANK,\
	TYPE_RESTAURANT, TYPE_TOWNHALL, TYPE_RADIO, TYPE_CHURCH = range(16)

	BUILDING_TYPE = {
			TYPE_CLOTHES: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_BOMB: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_HOSPITAL: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_MUSEUM: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_DISCO: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_ARCADE: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_CARPARK: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_FACTORY: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_OFFICE: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_PARK: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_WAREHOUSE: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_BANK: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_RESTAURANT: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_TOWNHALL: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_RADIO: (image.load('assets/building.png'), (0.114, 1)),
			TYPE_CHURCH: (image.load('assets/building.png'), (0.114, 1)),
			}

	def __init__(self, id, state=None):
		self.id = id
		self.type = self.TYPE_CLOTHES
		self.has_bomb = False
		self.blownup_cooldown = 0

		if state != None:
			(self.type, self.has_bomb, self.blownup_cooldown, self.door_location) = state

		self.sprite = sprite.Sprite(self.BUILDING_TYPE[self.type][0])
		self.sprite.x = 256 + 1 + 28 + 202 * (id % 4)
		self.sprite.y = 1 + 28 + 202 * (id / 4)
	
	def draw(self, window):
		self.sprite.draw()

	def update(self, time):
		pass

	def state(self):
		return (self.type, self.has_bomb, self.blownup_cooldown, self.door_location)

from Dude import *
