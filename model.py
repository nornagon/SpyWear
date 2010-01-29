import random
from pyglet import *

COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)

class World:
	def __init__(self):
		self.buildings = []
		self.dudes = []
		self.players = []
		self.background = image.load('assets/City.png')

	def draw(self, window):
		window.clear()

		# background
		self.background.blit(256,0)

		for d in self.dudes:
			d.draw(window)

		for p in self.players:
			p.draw(window)

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

		for p in self.players:
			p.update(time)

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


world = World()

#   8       9   10     11   12     13   14     15
# 7 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
# 6 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
# 5 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
# 4 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
# 3 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
# 2 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
# 1 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
#   |       |   |       |   |       |   |       |
# 0 +-------+---+-------+---+-------+---+-------+

class Dude:
	LEFT, RIGHT, UP, DOWN = range(4)
	HAT, COAT, SUIT = range(3)

	TURN_UP, TURN_DOWN, TURN_LEFT, TURN_RIGHT, ENTER_BUILDING = range(5)

	BUILDINGS_X = 4
	BUILDINGS_Y = 4

	DUDE_IMG = image.load('assets/man.png')
	DUDE_IMG.anchor_x = DUDE_IMG.width // 2
	DUDE_IMG.anchor_y = DUDE_IMG.height // 2

	def __init__(self):
		self.path = 0
		self.location = 0.0
		self.direction = self.RIGHT
		self.stopped = False
		self.outfit = self.HAT
		self.colour = COLOUR_RED
		
		self.has_bomb = False
		self.bomb_location = None

		self.mission_target = None
		self.score = 9001

		self.sprite = sprite.Sprite(self.DUDE_IMG)

	def draw(self, window):
		self.sprite.draw()

	def update(self, time):
		if self.path < self.BUILDINGS_Y*2:
			# on a horizontal path
			if self.path % 2 == 0:
				self.sprite.rotation = 90
				# south side of a building
				y = 14 + 202 * self.path/2
			else:
				self.sprite.rotation = 0
				# north side of a building
				y = 28 + 104 + 14 + 202 * self.path/2
			self.sprite.y = 1 + y
			self.sprite.x = 256 + 1 + 766 * self.location
		else:
			self.sprite.x = a
		pass
