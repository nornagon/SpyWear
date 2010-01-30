from pyglet import *
import random
from model import *

#   8       9   10     11   12     13   14     15
# 7 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |  12   |   |  13   |   |  14   |   |  15   |
#   |       |   |       |   |       |   |       |
# 6 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
# 5 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |   8   |   |   9   |   |  10   |   |  11   |
#   |       |   |       |   |       |   |       |
# 4 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
# 3 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |   4   |   |   5   |   |   6   |   |   7   |
#   |       |   |       |   |       |   |       |
# 2 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
# 1 +-------+---+-------+---+-------+---+-------+
#   |       |   |       |   |       |   |       |
#   |   0   |   |   1   |   |   2   |   |   3   |
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

LEFT, RIGHT, UP, DOWN = range(4)

class Dude:
	HAT, COAT, SUIT = range(3)

	TURN_UP, TURN_DOWN, TURN_LEFT, TURN_RIGHT, ENTER_BUILDING = range(5)

	DUDE_IMG = image.load('assets/man.png')
	DUDE_IMG.anchor_x = DUDE_IMG.width // 2
	DUDE_IMG.anchor_y = DUDE_IMG.height // 2

	# 1/sec where sec = time to walk from one side of the map to the other
	SPEED = 1/20.

	def __init__(self, id=None, batch=None, state=None):
		self.id = id
		self.path = 0
		self.location = 0.0
		self.direction = RIGHT
		self.next_direction = self.direction
		self.stopped = False
		self.outfit = self.HAT
		self.colour = 0
		
		self.has_bomb = False
		self.bomb_location = None

		self.mission_target = None
		self.score = 9001

		self.sprite = sprite.Sprite(self.DUDE_IMG, batch=batch)

		self.idle_time = 0.0

		if state != None:
			self.update_local_state(state)

		if self.id == None:
			raise Exception("Dude does not have an ID!")

	def state(self):
		return (self.id, self.path, self.location, self.direction, self.next_direction, self.stopped, self.outfit, self.colour, self.has_bomb, self.bomb_location, self.mission_target, self.score)

	def update_local_state(self, remotestate):
		(id, self.path, self.location, self.direction, self.next_direction, self.stopped, self.outfit, self.colour, self.has_bomb, self.bomb_location, self.mission_target, self.score) = remotestate
		if self.id is None:
			self.id = id
		elif id != self.id:
			raise Exception("dude ID does not match!")

	def update_remote_state(self):
		broadcast_dude_update(self.state())

	def randomise(self):
		self.location = random.random()
		self.path = random.randint(0, PATHS - 1)
		if left_right_path(self.path):
			self.direction = random.randint(LEFT, RIGHT)
			self.next_direction = self.direction
		else:
			self.direction = random.randint(UP, DOWN)
			self.next_direction = self.direction

	def draw(self, window):
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


	def forward(self):
		if self.direction == UP or self.direction == RIGHT:
			# going 'forwards'
			return True
		else:
			# ... or backwards...
			return False

	def turn(self, new_direction):
		if new_direction == self.opposite(self.direction):
			self.direction = new_direction
			self.next_direction = new_direction
		else:
			self.next_direction = new_direction

		self.update_remote_state()
 
	def stopstart(self):
		self.stopped = not self.stopped

	def enter(self):
		# self.path combined with location gives the building you are walking past
		if 0.018 < self.location < 0.190:
			building = 0
		elif 0.281 < self.location < 0.453:
			building = 1
		elif 0.544 < self.location < 0.716:
			building = 2
		elif 0.807 < self.location < 0.979:
			building = 3
		else:
			#not near a door
			return
		if self.path == 0 or self.path == 1:
			nearest_building = building

		elif self.path == 2 or self.path == 3:
			nearest_building = 4 +building

		elif self.path == 4 or self.path == 5:
			nearest_building = 8 + building

		elif self.path == 6 or self.path == 7:
			nearest_building = 12 + building

		elif self.path == 8 or self.path == 9:
			nearest_building = building * 4
			
		elif self.path == 10 or self.path == 11:
			nearest_building = building * 4 + 1
			
		elif self.path == 12 or self.path == 13:
			nearest_building = building * 4 + 2
			
		elif self.path == 14 or self.path == 15:
			nearest_building = building * 4 + 3
		print "I am near building ", nearest_building
		return nearest_building

	def bomb(self):
		# if in building, set bomb
		# if bomb in play, set off bomb
		# else error message
		pass
                
	def opposite(self, direction):
		if direction == LEFT:
			return RIGHT
		if direction == RIGHT:
			return LEFT
		if direction == UP:
			return DOWN
		if direction == DOWN:
			return UP

	# This function returns the next path which the dude will cross.
	def next_intersect(self):
		x = 0
		while PATH_INTERSECTS[x] < self.location and x < (BUILDINGS_X * 2 - 1):
			x += 1

		if not self.forward() and x > 0:
			x -= 1

		if left_right_path(self.path):
			x += BUILDINGS_X * 2

		return x

	def update(self, time):
		self.idle_time -= time
		if self.idle_time < 0: self.idle_time = 0

		if self.stopped:
			return

		corner = False
		if self.direction == RIGHT or self.direction == UP:
			# going from 0 to 1
			nextlocation = self.location + time * self.SPEED 
			if nextlocation > PATH_INTERSECTS[self.next_intersect()]:
				corner = True
				if self.direction != self.next_direction:
					# we have passed the intersect and are turning
					new_path = self.next_intersect()
					nextlocation = PATH_INTERSECTS[self.path]
					self.path = new_path
					self.direction = self.next_direction
			self.location = nextlocation   
		else:
			# going from 1 to 0
			nextlocation = self.location - time * self.SPEED 
			if nextlocation < PATH_INTERSECTS[self.next_intersect()]:
				corner = True
				if self.direction != self.next_direction:
					# we have passed the intersect and are turning
					new_path = self.next_intersect()
					nextlocation = PATH_INTERSECTS[self.path]
					self.path = new_path
					self.direction = self.next_direction
			self.location = nextlocation

