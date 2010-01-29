
COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)

class World:
	def __init__(self):
		self.buildings = []
		self.dudes = []
		self.players = []

	def draw(self):
		for b in self.buildings:
			b.draw()

		for d in dudes:
			d.draw()

		for p in players:
			p.draw()

	def update(self, time):
		for b in self.buildings:
			b.update(time)

		for d in dudes:
			d.update(time)

		for p in players:
			p.update(time)

class Building:
	TYPE_SHOP, TYPE_NONE = range(2)

	def __init__(self):
		self.type = NONE
		self.colour = RED
		self.has_bomb = False
	
	def draw(self):
		pass

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

	def draw(self):
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


