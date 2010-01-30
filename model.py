import random
from pyglet import *
import math
from Dude import *

COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)

class World:
	def __init__(self, state = None):
		self.buildings = []
		self.dudes = []
		self.dudes_batch = graphics.Batch()
		self.background = image.load('assets/City.png')
		self.hud_mockup = image.load('assets/hud_mockup.png')

		if state != None:
			(building_state, dude_state) = state
			self.buildings = [Building(s) for s in building_state]
			self.dudes = [Dude(s) for s in dude_state]

	def add_dude(self):
		d = Dude(batch = self.dudes_batch)
		d.randomise()
		self.dudes.append(d)

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
		return ([b.state() for b in buildings], [d.state for d in dudes])

class Building:
	TYPE_CLOTHES, TYPE_BOMB, TYPE_HOSPITAL, TYPE_MUSEUM, TYPE_DISCO, TYPE_ARCADE, TYPE_CARPARK, TYPE_FACTORY = range(8)

	SPRITES = {
			TYPE_CLOTHES: image.load('assets/building.png'),
			TYPE_BOMB: image.load('assets/building.png'),
			TYPE_HOSPITAL: image.load('assets/building.png'),
			TYPE_MUSEUM: image.load('assets/building.png'),
			TYPE_DISCO: image.load('assets/building.png'),
			TYPE_ARCADE: image.load('assets/building.png'),
			TYPE_CARPARK: image.load('assets/building.png'),
			TYPE_FACTORY: image.load('assets/building.png'),
			}

	def __init__(self, id, state=None):
		self.id = id
		self.type = self.TYPE_CLOTHES
		self.door_location = 0
		self.has_bomb = False
		self.blownup_cooldown = 0

		if state != None:
			(self.type, self.has_bomb, self.blownup_cooldown) = state

		self.sprite = sprite.Sprite(self.SPRITES[self.type])
		self.sprite.x = 256 + 1 + 28 + 202 * (id % 4)
		self.sprite.y = 1 + 28 + 202 * (id / 4)
	
	def draw(self, window):
		self.sprite.draw()

	def update(self, time):
		pass

	def state(self):
		return (self.type, self.has_bomb, self.blownup_cooldown)

