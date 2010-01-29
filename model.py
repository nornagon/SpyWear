import random
from pyglet import *
import random
import math

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

	def draw(self, window):
		window.clear()

		# background
		self.background.blit(256,0)

#		for d in self.dudes:
#			d.draw(window)
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
BUILDINGS_X = 4
BUILDINGS_Y = 4
PATHS = (BUILDINGS_X + BUILDINGS_Y) * 2

def left_right_path(path):
	return path < (BUILDINGS_X * 2)

def up_down_path(path):
	return not left_right_path(path)

def path_intersect(path):
	path %= BUILDINGS_X * 2
	path_inc = path / 2
	if path % 2 == 0:
		# south side of a building
		y = 14 + 202 * path_inc
	else:
		# north side of a building
		y = 28 + 104 + 14 + 202 * path_inc

	return y / 768.0

PATH_INTERSECTS = [path_intersect(x) for x in range(PATHS)]


class Dude:
	LEFT, RIGHT, UP, DOWN = range(4)
	HAT, COAT, SUIT = range(3)

	TURN_UP, TURN_DOWN, TURN_LEFT, TURN_RIGHT, ENTER_BUILDING = range(5)

	DUDE_IMG = image.load('assets/man.png')
	DUDE_IMG.anchor_x = DUDE_IMG.width // 2
	DUDE_IMG.anchor_y = DUDE_IMG.height // 2

	# 1/sec where sec = time to walk from one side of the map to the other
	SPEED = 1/20.
	#SPEED = 0

	def __init__(self, batch=None):
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

		self.sprite = sprite.Sprite(self.DUDE_IMG, batch=batch)
	
	def randomise(self):
		self.location = random.random()
		self.path = random.randint(0, PATHS - 1)
		if left_right_path(self.path):
			self.direction = random.randint(self.LEFT, self.RIGHT)
		else:
			self.direction = random.randint(self.UP, self.DOWN)

	def draw(self, window):
		self.sprite.draw()

	def forward(self):
		if self.direction % 2 == 0:
			# going 'forwards'
			return True
		else:
			# ... or backwards...
			return False

	# This function returns the next path which the dude will cross.
	def next_intersect(self):
		x = 0
		while PATH_INTERSECTS[x] < self.location:
			x += 1

		if not self.forward():
			x -= 1

	def update(self, time):
		if left_right_path(self.path):
			# on a horizontal path
			self.sprite.rotation = 90
			y = PATH_INTERSECTS[self.path] * 768.0
			self.sprite.y = 1 + y
			self.sprite.x = 256 + 1 + 766 * self.location
		else:
			# on a vertical path
			self.sprite.rotation = 0
			x = PATH_INTERSECTS[self.path] * 768.0
			self.sprite.x = 256 + 1 + x
			self.sprite.y = 1 + 766 * self.location

		if self.forward():
			# going 'forwards'
			self.location += time * self.SPEED
		else:
			# ... or backwards...
			self.location -= time * self.SPEED
