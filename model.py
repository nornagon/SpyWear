import random
from pyglet import *
import math

COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)

class World:
	def __init__(self, state = None):
		self.buildings = []
		self.dudes = []
		self.dudes_batch = graphics.Batch()
		self.background = image.load('assets/City.png')
		self.hud_mockup = image.load('assets/hud_mockup.png')

		self.players = [None, None, None, None]

		if state is None:
			# init
			for i in xrange(16):
				self.buildings.append(Building(i))

			for i in xrange(20):
				self.add_dude()

			global my_player_id
			my_player_id = self.allocate_new_playerid()
		else:
			# construct from given state
			(building_state, dude_state) = state

			for i in xrange(len(building_state)):
				self.buildings.append(Building(i, building_state[i]))

			self.dudes = [Dude(batch=self.dudes_batch, state=s) for s in dude_state]

	def allocate_new_playerid(self):
		if not None in self.players:
			return None

		player_id = self.players.index(None)

		if player_id > len(self.dudes):
			print "No dudes to take control of!"
			return None

		self.players[player_id] = player_id
		self.dudes[player_id].take_control_by(player_id)


	def add_dude(self):
		d = Dude(id = len(self.dudes), batch = self.dudes_batch)
		d.randomise()
		self.dudes.append(d)

	def get_player(self, my_player_id):
		return self.dudes[my_player_id]

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

	SPRITES = {
			TYPE_CLOTHES: image.load('assets/building.png'),
			TYPE_BOMB: image.load('assets/building.png'),
			TYPE_HOSPITAL: image.load('assets/building.png'),
			TYPE_MUSEUM: image.load('assets/building.png'),
			TYPE_DISCO: image.load('assets/building.png'),
			TYPE_ARCADE: image.load('assets/building.png'),
			TYPE_CARPARK: image.load('assets/building.png'),
			TYPE_FACTORY: image.load('assets/building.png'),
			TYPE_OFFICE: image.load('assets/building.png'),
			TYPE_PARK: image.load('assets/building.png'),
			TYPE_WAREHOUSE: image.load('assets/building.png'),
			TYPE_BANK: image.load('assets/building.png'),
			TYPE_RESTAURANT: image.load('assets/building.png'),
			TYPE_TOWNHALL: image.load('assets/building.png'),
			TYPE_RADIO: image.load('assets/building.png'),
			TYPE_CHURCH: image.load('assets/building.png')
			}

#     0  1  2        
#    |-------|
# 11 |       | 3
#    |       |
# 10 |       | 4
#    |       |
#  9 |       | 5
#    |-------|
#     8  7  6

	door_locations = {
                }

	def __init__(self, id, state=None):
		self.id = id
		self.type = self.TYPE_CLOTHES
		self.door_location = 0
		self.has_bomb = False
		self.blownup_cooldown = 0

		if state != None:
			(self.type, self.has_bomb, self.blownup_cooldown, self.door_location) = state

		self.sprite = sprite.Sprite(self.SPRITES[self.type])
		self.sprite.x = 256 + 1 + 28 + 202 * (id % 4)
		self.sprite.y = 1 + 28 + 202 * (id / 4)
	
	def draw(self, window):
		self.sprite.draw()

	def update(self, time):
		pass

	def state(self):
		return (self.type, self.has_bomb, self.blownup_cooldown, self.door_location)

from Dude import *
