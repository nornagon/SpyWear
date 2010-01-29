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

		self.background.blit(256,0)

		label = text.Label("FPS: %d" % clock.get_fps(), font_name="Georgia",
				font_size=24, x=0, y=7)
		label.draw()

		for b in self.buildings:
			b.draw(window)

		for d in self.dudes:
			d.draw(window)

		for p in self.players:
			p.draw(window)

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

class Dude:
	LEFT, RIGHT, UP, DOWN = range(4)
	HAT, COAT, SUIT = range(3)

	TURN_UP, TURN_DOWN, TURN_LEFT, TURN_RIGHT, ENTER_BUILDING = range(5)

	def __init__(self):
		self.location = (0.5, 0.5)
		self.direction = RIGHT
		self.stopped = False
		self.outfit = HAT
		self.colour = RED

	def draw(self, window):
		pass

	def update(self, time):
		pass


class Player(Dude):
	BOMB_NONE, BOMB_INVENTORY, BOMB_BUILDING = range(3)

	def __init__(self):
		super(Player, self).__init__(self)
		
		self.bomb = BOMB_NONE
		self.bomb_location = None

		self.mission_target = None
		self.score = 9001

	def update(self, time):
		pass


