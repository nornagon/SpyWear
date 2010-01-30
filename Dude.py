from pyglet import *
import random
from model import *
import glob, os

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

ROT_UP, ROT_RIGHT, ROT_DOWN, ROT_LEFT = range(4)
TRANS = {LEFT: ROT_LEFT, RIGHT: ROT_RIGHT, UP: ROT_UP, DOWN: ROT_DOWN}
INV_TRANS = dict (zip(TRANS.values(),TRANS.keys()))

class Dude:
	HAT, COAT, SUIT = range(3)

	def load_anim(path, fps):
		jn = os.path.join
		files = glob.glob(jn('assets', path, '*.png'))
		files.sort()
		images = [image.load(f) for f in files]
		for img in images:
			img.anchor_x = img.width // 2
			img.anchor_y = img.height // 2
		return image.Animation.from_image_sequence(images, 1.0/fps)

	DUDE_IMG = load_anim('Guy_walking_greenJ_blond', 24)

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
		self.halo = None
		#if self.is_active_player():
			#self.halo = sprite.Sprite(self.DUDE_HALO, batch=batch)

		self.player_id = None

		self.idle_time = 0.0

		if state != None:
			self.update_local_state(state)

		if self.id == None:
			raise Exception("Dude does not have an ID!")

		self.workout_next_direction()
	
	def take_control_by(self, player_id, suppressUpdate=False):
		print "dude", self.id, "controlled by", player_id
		self.player_id = player_id
		self.next_direction = self.direction
		self.idle_time = 0.0
		self.score = 0
		self.stopped = False
		if not suppressUpdate:
			self.update_remote_state()

	def state(self):
		return (self.id, self.path, self.location, self.direction, self.next_direction, self.stopped, self.outfit, self.colour, self.has_bomb, self.bomb_location, self.mission_target, self.score, self.player_id)

	def update_local_state(self, remotestate):
		(id, self.path, self.location, self.direction, self.next_direction, self.stopped, self.outfit, self.colour, self.has_bomb, self.bomb_location, self.mission_target, self.score, self.player_id) = remotestate
		if self.id is None:
			self.id = id
		elif id != self.id:
			raise Exception("dude ID does not match!")

	def update_remote_state(self):
		broadcast_dude_update(self.state())

	def is_active_player(self):
		return World.my_player_id == self.id

	def randomise(self):
		self.location = random.random()
		self.path = random.randint(0, PATHS - 1)
		if left_right_path(self.path):
			self.direction = random.randint(LEFT, RIGHT)
			self.next_direction = self.direction
		else:
			self.direction = random.randint(UP, DOWN)
			self.next_direction = self.direction

		self.workout_next_direction()

		self.update_remote_state()

	def draw(self, window):
		if self.direction == LEFT:
			self.sprite.rotation = -90
		elif self.direction == RIGHT:
			self.sprite.rotation = 90
		elif self.direction == UP:
			self.sprite.rotation = 0
		elif self.direction == DOWN:
			self.sprite.rotation = 180
		if left_right_path(self.path):
			# on a horizontal path
			y = PATH_INTERSECTS[self.path] * 768.0
			self.sprite.y = 1 + y
			self.sprite.x = 256 + 1 + 766 * self.location
		else:
			# on a vertical path
			x = PATH_INTERSECTS[self.path] * 768.0
			self.sprite.x = 256 + 1 + x
			self.sprite.y = 1 + 766 * self.location

		#if self.halo:
			#self.halo.rotation = self.sprite.rotation
			#self.halo.x = self.sprite.x
			#self.halo.y = self.sprite.y


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

		self.stopped = False

		self.update_remote_state()
 
	def stopstart(self):
		self.stopped = not self.stopped
		self.update_remote_state()

	def enter(self):
		pass
		
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


	def valid_next_directions(self):
		next_intersect_id = self.next_intersect()
		if next_intersect_id >= 8:
			next_intersect_id -= 8

		if self.path < BUILDINGS_X * 2:
			y, x = self.path, next_intersect_id
		else:
			x, y = self.path - 8, next_intersect_id

		valid_directions = []

		if x > 0:
			valid_directions.append(LEFT)
		if x < 7:
			valid_directions.append(RIGHT)
		if y > 0:
			valid_directions.append(DOWN)
		if y < 7:
			valid_directions.append(UP)

		return valid_directions

	def workout_next_direction(self):
#		print "workout next direction. direction:", self.direction
		directions = self.valid_next_directions()
#		print "valid directions:", directions
		directions.sort()
#		self.next_direction = directions[0]
		self.turn(random.choice(directions))
		self.update_remote_state()

	def update(self, time):
		self.idle_time -= time
		if self.idle_time < 0: self.idle_time = 0

		if self.stopped:
			return

		if self.direction == RIGHT or self.direction == UP:
			# going from 0 to 1
			forwards = True
			nextlocation = self.location + time * self.SPEED 
		else:
			# going from 1 to 0
			forwards = False
			nextlocation = self.location - time * self.SPEED 

		next_path_intersect = PATH_INTERSECTS[self.next_intersect()]

		if (forwards and nextlocation > next_path_intersect) \
			or (not forwards and nextlocation < next_path_intersect):
			if self.direction != self.next_direction:
				# we have passed the intersect and are turning
				new_path = self.next_intersect()
				nextlocation = PATH_INTERSECTS[self.path]
				self.path = new_path
				self.direction = self.next_direction
			if self.player_id is None and World.is_server:
				self.workout_next_direction()

		if nextlocation < PATH_INTERSECTS[0]:
			nextlocation = PATH_INTERSECTS[0]
		elif nextlocation > PATH_INTERSECTS[7]:
			nextlocation = PATH_INTERSECTS[7]
		self.location = nextlocation   


from net import broadcast_dude_update
