import random
from pyglet import *
import math
from Dude import *

COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)

class World:
	def __init__(self):
		self.buildings = []
		self.dudes = []
		self.dudes_batch = graphics.Batch()
		self.background = image.load('assets/City.png')

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

class Building:
	TYPE_SHOP, TYPE_NONE = range(2)

	SPRITES = [
			image.load('assets/building.png'),
			]

	def __init__(self, id):
		self.id = id
		self.sprite = sprite.Sprite(random.choice(self.SPRITES))
		self.sprite.x = 256 + 1 + 28 + 202 * (id % 4)
		self.sprite.y = 1 + 28 + 202 * (id / 4)
		self.type = self.TYPE_NONE
		self.has_bomb = False
	
	def draw(self, window):
		self.sprite.draw()

	def update(self, time):
		pass

