from pyglet import *
import random
from model import *
import anim

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

HAT, NO_HAT = range(2)
BLUE, YELLOW, GREEN = range(3)

class Dude:
	DUDE_OUTFITS = {
		(HAT, BLUE): anim.load_anim('guy_walking_blue_hat'),
		(NO_HAT, BLUE): anim.load_anim('guy_walking_blue_noHat'),
		(HAT, YELLOW): anim.load_anim('guy_walking_yellow_noHat'),
		(NO_HAT, YELLOW): anim.load_anim('guy_walking_yellow_hat'),
		(HAT, GREEN): anim.load_anim('guy_walking_green_hat'),
		(NO_HAT, GREEN): anim.load_anim('guy_walking_green_noHat'),
	}
	DUDE_MARKER = anim.load_anim('Rings', 18)

	# 1/sec where sec = time to walk from one side of the map to the other
	SPEED = 1/20.

	def __init__(self, id=None, batch=None, state=None):
		self.id = id
		self.path = 0
		self.location = 0.0
		self.direction = RIGHT
		self.next_direction = self.direction
		self.stopped = False
		self.outfit = HAT
		self.colour = BLUE
		self.batch = batch
		self.is_in_building = False
		self.building_id = None
		self.building_direction = UP
		self.building_cooldown = 0.0
		
		self.has_bomb = False
		self.bomb_location = None

		self.mission_target = None
		self.score = 9001

		self.sprite = sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
				batch=batch, group=anim.GROUND)
		self.marker = None
		if self.is_active_player():
			self.marker = sprite.Sprite(self.DUDE_MARKER, batch=batch,
					group=anim.MARKER)

		self.player_id = None

		self.idle_time = 0.0

		if state != None:
			self.update_local_state(state)

		if self.id == None:
			raise Exception("Dude does not have an ID!")

		self.workout_next_direction()

	def xy(self):
		if left_right_path(self.path):
			# on a horizontal path
			y = PATH_INTERSECTS[self.path] * 768
			x = 768 * self.location
		else:
			# on a vertical path
			x = PATH_INTERSECTS[self.path] * 768
			y = 768 * self.location

		return (x,y)
	
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
		self.outfit = random.choice([HAT, NO_HAT])
		self.colour = random.choice([BLUE, YELLOW, GREEN])
		self.sprite = sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
				batch=self.batch, group=anim.GROUND)


	def draw(self, window):
		if self.direction == LEFT:
			self.sprite.rotation = -90
		elif self.direction == RIGHT:
			self.sprite.rotation = 90
		elif self.direction == UP:
			self.sprite.rotation = 0
		elif self.direction == DOWN:
			self.sprite.rotation = 180
		#self.halo.rotation = self.sprite.rotation
		if self.is_in_building:
			if self.building_cooldown > 2.:
				# go in
				offset = ((4. - self.building_cooldown)/2.) * 66
				entering = True
			else:
				# go out
				offset = self.building_cooldown/2. * 66
				entering = False

			if self.building_direction == UP:
				# on a horizontal path
				y = PATH_INTERSECTS[self.path] * 768.0
				self.sprite.x = 256 + 1 + 766 * self.location
				self.sprite.y = 1 + y + offset
				if entering:
					self.direction = UP
				else:
					self.direction = DOWN
				
			if self.building_direction == DOWN:
				y = PATH_INTERSECTS[self.path] * 768.0
				self.sprite.x = 256 + 1 + 766 * self.location
				self.sprite.y = 1 + y - offset
				if entering:
					self.direction = DOWN
				else:
					self.direction = UP

			if self.building_direction == LEFT:
				pass
			if self.building_direction == RIGHT:
				pass
				
		elif left_right_path(self.path):
			# on a horizontal path
			y = PATH_INTERSECTS[self.path] * 768.0
			self.sprite.y = 1 + y
			self.sprite.x = 256 + 1 + 768 * self.location
		else:
			# on a vertical path
			x = PATH_INTERSECTS[self.path] * 768.0
			self.sprite.x = 256 + 1 + x
			self.sprite.y = 1 + 768 * self.location

		if self.marker:
			self.marker.rotation = self.sprite.rotation
			self.marker.x = self.sprite.x
			self.marker.y = self.sprite.y


	def forward(self):
		if self.direction == UP or self.direction == RIGHT:
			# going 'forwards'
			return True
		else:
			# ... or backwards...
			return False

	def turn(self, new_direction):
		if not self.is_in_building:
			if new_direction == self.opposite(self.direction):
				self.direction = new_direction
				self.next_direction = new_direction
			else:
				self.next_direction = new_direction

			self.stopped = False

			self.update_remote_state()
 
	def stopstart(self):
		if not self.is_in_building:
			self.stopped = not self.stopped
			self.update_remote_state()

	def enter(self):
		if not self.is_in_building:
			# Use self.path and self.location to see if we're near a door
			i = 0
			for (door_path, door_location) in World.get_world().doors:
				if door_path == self.path and (door_location - 0.057) < self.location < door_location:
					# Player is at a door and may enter
					self.is_in_building = True
					self.building_id = i
					self.building_cooldown = 4.0
					# Even is up or right, Odd is down or left
					if self.path < 8 and self.path % 2 == 0:
						# Go up
						self.building_direction = UP
					elif self.path < 8 and self.path % 2 == 1:
						# Go down (on your mother)
						self.building_direction = DOWN
					elif self.path >= 8 and self.path % 2 == 0:
						# Go right
						self.building_direction = RIGHT
					elif self.path >= 8 and self.path % 2 == 1:
						# Go left
						self.building_direction = LEFT
					print "Player has entered building ", i, " going ", self.building_direction
				i += 1
		
	def bomb(self):
		# if in building, set bomb
		if self.is_in_building and self.has_bomb:
			self.bomb_location = self.building_id
			print "laid bomb in building ", self.building_id
		
		# if bomb in play, set off bomb
		elif self.bomb_location != None:
			print "Set off bomb in building ", self.bomb_location
			World.get_world().buildings[self.bomb_location].explode()

			self.bomb_location = None
		
		# no bomb
		else:
			print "Player has no bomb, tried to set one off"
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
		if self.path < BUILDINGS_X * 2:
			x, y = self.path, next_intersect_id
		else:
			y, x = self.path, next_intersect_id

		valid_directions = []

		if x > 0:
			valid_directions.append(ROT_LEFT)
		if x < 7:
			valid_directions.append(ROT_RIGHT)
		if y > 0:
			valid_directions.append(ROT_DOWN)
		if y < 7:
			valid_directions.append(ROT_UP)

		rot_direction = TRANS[self.direction]
		valid_directions = [((d - rot_direction) % 4) for d in valid_directions]

		return [INV_TRANS[d] for d in valid_directions]

	def workout_next_direction(self):
		self.next_direction = self.valid_next_directions()[0]

	def update(self, time):
		self.idle_time -= time
		if self.idle_time < 0: self.idle_time = 0
		
		if self.is_in_building:
			start_time = self.building_cooldown
			self.building_cooldown -= time
			if start_time >= 2.0 and self.building_cooldown < 2.0:
				# End point of building travel. Buy from shop
				if World.get_world().buildings[self.building_id].type == Building.TYPE_CLOTHES:
					# in a clothes store, get random clothes
					self.outfit = random.choice([HAT, NO_HAT])
					self.colour = random.choice([BLUE, YELLOW, GREEN])
					self.sprite = sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
							batch=self.batch, group=anim.GROUND)
					print "Changed clothes to ", self.outfit, self.colour
				elif World.get_world().buildings[self.building_id].type == Building.TYPE_BOMB:
					# in a bomb store
					if self.has_bomb == False and self.bomb_location == None:
						# purchase a bomb
						print "Picked up a bomb"
						self.has_bomb = True
			if self.building_cooldown < 0:
				print "finished in building, moving on"
				self.is_in_building = False
				if self.building_direction == UP or self.building_direction == DOWN:
					self.direction = RIGHT
				else:
					self.direction = UP
				return
			return
		if self.stopped:
			return

		corner = False
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
			corner = True
			if self.direction != self.next_direction:
				# we have passed the intersect and are turning
				new_path = self.next_intersect()
				nextlocation = PATH_INTERSECTS[self.path]
				self.path = new_path
				self.direction = self.next_direction
				if self.player_id is None:
					self.workout_next_direction()

		if nextlocation < 0:
			nextlocation = 0
		elif nextlocation > 1:
			nextlocation = 1
		self.location = nextlocation   


from net import broadcast_dude_update
