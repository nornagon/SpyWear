from pyglet import *
import random
from model import *
import anim
import math

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

DOOR_OPEN_SOUND = resource.media('assets/Door Open.wav', streaming=False)
DOOR_CLOSE_SOUND = resource.media('assets/Door Close.wav', streaming=False)
LAUGH1_SOUND = resource.media('assets/Manic Laugh.wav', streaming=False)
LAUGH2_SOUND = resource.media('assets/Evil Laugh.wav', streaming=False)
ARM_BOMB_SOUND = resource.media('assets/Arming Bomb.wav', streaming=False)
CASH_SOUND = resource.media('assets/Cash Register.wav', streaming=False)
KILL_SOUND = resource.media('assets/Pistol Kill.wav', streaming=False)

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

ROT_UP, ROT_RIGHT, ROT_DOWN, ROT_LEFT = range(4)
TRANS = {LEFT: ROT_LEFT, RIGHT: ROT_RIGHT, UP: ROT_UP, DOWN: ROT_DOWN}
INV_TRANS = dict (zip(TRANS.values(),TRANS.keys()))

class Dude:
	DUDE_OUTFITS = {
		(HAT, BLUE): anim.load_anim('guy_walking_blue_hat'),
		(NO_HAT, BLUE): anim.load_anim('guy_walking_blue_noHat'),
		(HAT, YELLOW): anim.load_anim('guy_walking_yellow_hat'),
		(NO_HAT, YELLOW): anim.load_anim('guy_walking_yellow_noHat'),
		(HAT, GREEN): anim.load_anim('guy_walking_green_hat'),
		(NO_HAT, GREEN): anim.load_anim('guy_walking_green_noHat'),
	}
	DUDE_DEATHS = {
		(HAT, BLUE): anim.load_anim('guy_dieing_blue_hat', loop=False),
		(NO_HAT, BLUE): anim.load_anim('guy_dieing_blue_noHat', loop=False),
		(HAT, YELLOW): anim.load_anim('guy_dieing_yellow_noHat', loop=False),
		(NO_HAT, YELLOW): anim.load_anim('guy_dieing_yellow_hat', loop=False),
		(HAT, GREEN): anim.load_anim('guy_dieing_green_hat', loop=False),
		(NO_HAT, GREEN): anim.load_anim('guy_dieing_green_noHat', loop=False),
	}

	DUDE_MARKER = anim.load_anim('Rings', 18)
	BOMB_MARKER = anim.load_anim('Bomb_Marker', 12)
	TURN_MARKER = image.load('assets/turn_arrow.png')
	TURN_MARKER.anchor_x = TURN_MARKER.width // 2
	TURN_MARKER.anchor_y = TURN_MARKER.height // 2
	TURN_MARKER_FLIP = TURN_MARKER.texture.get_transform(flip_x = True)

	# 1/sec where sec = time to walk from one side of the map to the other
	SPEED = 1/15.

	def reset(self):
		self.path = 0
		self.location = 0.0
		self.direction = RIGHT
		self.next_direction = self.direction
		self.stopped = False
		self.outfit = HAT
		self.colour = BLUE
		self.is_in_building = False
		self.building_id = None
		self.building_direction = UP
		self.building_cooldown = 0.0

		self.shot_cooldown = 0.0
		
		self.has_bomb = False
		#self.has_bomb = True
		self.bomb_location = None

		self.alive = True
		self.fading = False

		self.idle_time = 0.0

		self.time_to_enter = random.random() * 20 + 3

	def __init__(self, id=None, state=None):
		self.id = id
		self.player_id = None

		self.reset()

		self.marker = None

		self.sprite = sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
				batch=World.batch, group=anim.GROUND)

		if state != None:
			self.update_local_state(state)

		if self.id == None:
			raise Exception("Dude does not have an ID!")

		self.workout_next_direction()

	def state(self):
		return (self.id, self.path, self.location, self.direction,
				self.next_direction, self.stopped, self.outfit, self.colour,
				self.has_bomb, self.bomb_location, self.player_id,
				self.alive, self.building_id, self.building_direction, self.building_cooldown,
				self.is_in_building)

	def update_local_state(self, remotestate):
		old_alive = self.alive
		old_outfit = self.outfit
		old_colour = self.colour

		(id, self.path, self.location, self.direction,
				self.next_direction, self.stopped, self.outfit, self.colour,
				self.has_bomb, self.bomb_location, self.player_id,
				self.alive, self.building_id, self.building_direction, self.building_cooldown,
				self.is_in_building) = remotestate

		if self.alive and (old_alive != self.alive or old_outfit != self.outfit or old_colour != self.colour):
			self.update_sprite()

		if (self.player_id != None):
			player = self.get_player()
			if player != None:
				player.update_dude_sprites()

		if self.id is None:
			self.id = id
		elif id != self.id:
			raise Exception("dude ID does not match!")



	def respawn(self):
		if not self.am_incharge():
			return

		self.reset()

		# pick a door to come out of
		building_id = random.randint(0,15)
		self.path, self.location = World.get_world().doors[building_id]
		if self.path >= 8:
			self.direction = random.choice([UP,DOWN])
		else:
			self.direction = random.choice([LEFT,RIGHT])
		self.next_direction = None

		self.random_outfit(suppressUpdate = True)
		self.enter(suppressUpdate = True)
		self.building_cooldown = 2.
		self.update_remote_state()

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

	def reset_idle_timer(self):
		self.idle_time = 20.0
	
	def take_control_by(self, player_id, suppressUpdate=False):
#		print "dude", self.id, "controlled by", player_id
		self.player_id = player_id
		self.next_direction = self.direction
		self.idle_time = 0.0
		self.stopped = False
		if not suppressUpdate:
			self.update_remote_state()

	def update_remote_state(self):
		broadcast_dude_update(self.state())

	def is_active_player(self):
		return World.my_player_id == self.id

	def am_incharge(self):
		return self.is_active_player() or (World.is_server and self.player_id == None)

	def set_sprite(self, spr):
		if self.sprite:
			self.sprite.delete()
		self.sprite = spr
		self.sprite.visible = True

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

		self.set_sprite(sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
				batch=World.batch, group=anim.GROUND))

		self.workout_next_direction()

		self.update_remote_state()

	def draw(self, window):
		if not self.marker and self.is_active_player():
			self.marker = sprite.Sprite(self.DUDE_MARKER, batch=World.batch,
					group=anim.MARKER)
			self.turn_marker = sprite.Sprite(self.TURN_MARKER, batch=World.batch, group=anim.PATH)
			self.turn_marker.visible = False
			self.turn_marker_flip = sprite.Sprite(self.TURN_MARKER_FLIP, batch=World.batch, group=anim.PATH)
			self.turn_marker_flip.visible = False


		effective_direction = self.direction
		if self.is_in_building:
			effective_direction = self.building_direction

		if effective_direction == LEFT:
			self.sprite.rotation = -90
		elif effective_direction == RIGHT:
			self.sprite.rotation = 90
		elif effective_direction == UP:
			self.sprite.rotation = 0
		elif effective_direction == DOWN:
			self.sprite.rotation = 180

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

			elif self.building_direction == DOWN:
				y = PATH_INTERSECTS[self.path] * 768.0
				self.sprite.x = 256 + 1 + 766 * self.location
				self.sprite.y = 1 + y - offset

			# TODO
			if self.building_direction == LEFT:
				pass
			if self.building_direction == RIGHT:
				pass
				
		else:
			if left_right_path(self.path):
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

			if self.next_direction != None and self.next_direction != self.direction and \
					self.next_direction != self.opposite(self.direction) and not self.is_in_building:
				xrow, yrow = self.destination_row_coordinates()
				x = PATH_INTERSECTS[xrow] * 768 + 256
				y = PATH_INTERSECTS[yrow] * 768
				if self.next_direction == LEFT and self.direction == DOWN:
					m = self.turn_marker
					m.rotation = 180
				elif self.next_direction == UP and self.direction == LEFT:
					m = self.turn_marker
					m.rotation = -90
				elif self.next_direction == DOWN and self.direction == RIGHT:
					m = self.turn_marker
					m.rotation = 90
				elif self.next_direction == RIGHT and self.direction == UP:
					m = self.turn_marker
					m.rotation = 0
				elif self.next_direction == RIGHT and self.direction == DOWN:
					m = self.turn_marker_flip
					m.rotation = 180
				elif self.next_direction == DOWN and self.direction == LEFT:
					m = self.turn_marker_flip
					m.rotation = -90
				elif self.next_direction == UP and self.direction == RIGHT:
					m = self.turn_marker_flip
					m.rotation = 90
				elif self.next_direction == LEFT and self.direction == UP:
					m = self.turn_marker_flip
					m.rotation = 0

				for b in [self.turn_marker, self.turn_marker_flip]:
					if m is b:
						b.visible = True
					else:
						b.visible = False
				m.x = x
				m.y = y
			else:
				self.turn_marker.visible = False
				self.turn_marker_flip.visible = False


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

	def enter(self, suppressUpdate = False):
		if not self.is_in_building:
			# Use self.path and self.location to see if we're near a door
			i = 0
			for (door_path, door_location) in World.get_world().doors:
				if door_path == self.path and door_location - 0.039 < self.location < door_location + 0.039 and not World.get_world().buildings[i].destroyed:
					# Player is at a door and may enter
					DOOR_OPEN_SOUND.play()
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
#					print "Player has entered building ", i, " going ", self.building_direction
					if not suppressUpdate:
						self.update_remote_state()
				i += 1
		
	def bomb(self):
		# if in building, set bomb
		if self.is_in_building and self.has_bomb:
			self.bomb_location = self.building_id
			self.bomb_marker = sprite.Sprite(self.BOMB_MARKER, batch=World.batch,
					group=anim.SKY)
			self.bomb_marker.x, self.bomb_marker.y = World.get_world().buildings[self.bomb_location].screen_coords()
			def do_fade(dt):
				self.bomb_marker.opacity -= 300*dt
				if self.bomb_marker.opacity <= 0:
					self.bomb_marker.delete()
					self.bomb_marker = None
					clock.unschedule(do_fade)
			def start_fade(dt):
				clock.schedule_interval(do_fade, 1/60.0)
			clock.schedule_once(start_fade, 1.5)

			self.has_bomb = False
			ARM_BOMB_SOUND.play()
#			print "laid bomb in building ", self.building_id
		
		# if bomb in play, set off bomb
		elif self.bomb_location != None and self.alive:
#			print "Set off bomb in building ", self.bomb_location
			World.get_world().buildings[self.bomb_location].explode(self.id)
			self.has_bomb = False
			if not (self.is_in_building and self.building_id == self.bomb_location):
				laugh = random.choice([LAUGH1_SOUND, LAUGH2_SOUND])
				clock.schedule_once(lambda dt: laugh.play(), 1.0)
			self.bomb_location = None
		# no bomb
#			print "Player has no bomb, tried to set one off"

	def shoot(self):
		if self.shot_cooldown > 0 or not self.alive: return
		dead_guy = World.get_world().nearest_dude_to(self)
		if not dead_guy: return
		broadcast_die(World.my_player_id, dead_guy.id)
		dead_guy.die()
		KILL_SOUND.play()
		if dead_guy.player_id == None:
			# Killed a Civilian, send out hint about player
			if random.random() < 0.5:
				broadcast_hint(self.id, 'appearance')
			else:
				broadcast_hint(self.id, 'mission')
		else:
			# Killed a Player
			World.get_world().set_score(self.id)
		self.shot_cooldown = 5.

	def die(self):
		self.set_sprite(sprite.Sprite(self.DUDE_DEATHS[(self.outfit,self.colour)],
				batch=World.batch, group=anim.GROUND))
		@self.sprite.event
		def on_animation_end():
			self.fading = True
		self.alive = False

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
		if self.location in PATH_INTERSECTS:
#			print "in intersects"
			x = PATH_INTERSECTS.index(self.location)
		else:
			x = 0

			while PATH_INTERSECTS[x] < self.location and x < (BUILDINGS_X * 2 - 1):
				x += 1

			if not self.forward() and x > 0:
				x -= 1

		if left_right_path(self.path):
			x += BUILDINGS_X * 2

		return x

	def in_intersect(self):
		return self.location in PATH_INTERSECTS

	def destination_row_coordinates(self):
		next_intersect_id = self.next_intersect()
		if next_intersect_id >= 8:
			next_intersect_id -= 8

		if self.path < BUILDINGS_X * 2:
			y, x = self.path, next_intersect_id
		else:
			x, y = self.path - 8, next_intersect_id

		return (x, y)

	def valid_next_directions(self):
		x, y = self.destination_row_coordinates()

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
#		print "workout next direction. Old direction:", self.direction
		directions = self.valid_next_directions()
#		print "valid directions:", directions
#		self.next_direction = directions[0]
		self.next_direction = random.choice(directions)
		self.update_remote_state()

	# do movement update.
	def movement_update_helper(self, time):
		frame_distance = time * self.SPEED

		if self.forward():
			# going from 0 to 1
			nextlocation = self.location + frame_distance
		else:
			# going from 1 to 0
			nextlocation = self.location - frame_distance
		
		while True:
			# Few cases:
			# - We're at an intersection: (optionally) turn, figure out new next_direction
			# - We're going along a straight path. Just move to next intersection

			# Pump the next_direction
			if self.in_intersect() and self.next_direction != None:
#				print "Turning in intersection. Should only happen once per corner"

				intersect = self.next_intersect()

				# ... just for debugging
#				x, y = self.destination_row_coordinates()
#				print "We are at %d, %d on path %d going direction %d. Next intersect at %d" % (x, y, self.path, self.direction, intersect)

				if self.direction != self.next_direction:
					if self.next_direction == self.opposite(self.direction):
						self.direction = self.next_direction
					else:
						self.direction = self.next_direction
						self.location = PATH_INTERSECTS[self.path]
						self.path = intersect

				self.next_direction = None

#				x, y = self.destination_row_coordinates()
#				print "We are at %d, %d on path %d going direction %d. Next intersect at %d" % (x, y, self.path, self.direction, intersect)

			if self.in_intersect() and self.next_direction == None:
#				print "Moving away from intersect by %f" % frame_distance

				if self.forward():
					self.location += frame_distance
				else:
					self.location -= frame_distance

				if (self.player_id is None and World.is_server) or \
						(self.is_active_player() and (self.idle_time == 0. or \
							(not self.direction in self.valid_next_directions()))):
#					print "workout"
					self.workout_next_direction()

				return

			if not self.in_intersect():
#				print "between intersect. Moving forward..."

				intersect = self.next_intersect()
				next_path_intersect = PATH_INTERSECTS[intersect]

				if (self.forward() and nextlocation > next_path_intersect) \
					or (not self.forward() and nextlocation < next_path_intersect):
						# Just advance to the intersect
					pre_distance = abs(self.location - next_path_intersect)
					post_distance = frame_distance - pre_distance

					# now advance to the intersect
					self.location = next_path_intersect
					frame_distance = post_distance
				else:
					if self.forward():
						self.location += frame_distance
					else:
						self.location -= frame_distance

					return

	def get_player(self):
		if self.player_id == None:
			return None

		world = World.get_world()
		if world == None:
			return None
		else:
			return world.players[self.player_id]

	def update_sprite(self):
		self.set_sprite(sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
				batch=World.batch, group=anim.GROUND))
		self.sprite.visible = True
		self.fading = False
		self.sprite.opacity = 255

	def random_outfit(self, suppressUpdate = False):
		self.outfit = random.choice([HAT, NO_HAT])

		colours = [BLUE, YELLOW, GREEN]
		colours.remove(self.colour)
		self.colour = random.choice(colours)
		self.update_sprite()
#		print "Changed clothes to ", self.outfit, self.colour

		if (self.player_id != None):
			self.get_player().update_dude_sprites()

		if not suppressUpdate:
			self.update_remote_state()


	def update(self, time):
		if not self.alive:
			if self.fading:
				self.sprite.opacity -= time * 100
				if self.sprite.opacity <= 0:
					self.sprite.opacity = 255
					self.sprite.visible = False
					self.fading = False
					if self.am_incharge():
						clock.schedule_once(lambda dt: self.respawn(), 5)
			return

		if World.is_server and self.player_id is None:
			self.time_to_enter -= time
			if self.time_to_enter <= 0:
				self.enter()
				self.time_to_enter = random.random() * 20 + 3

		self.idle_time -= time
		if self.idle_time < 0: self.idle_time = 0

		if self.shot_cooldown > 0:
			self.shot_cooldown -= time
			if self.shot_cooldown < 0:
				self.shot_cooldown = 0

		if self.is_in_building:
			start_time = self.building_cooldown

			self.building_cooldown -= time
			if start_time >= 2.0 and self.building_cooldown < 2.0:
				self.sprite.visible = True
				# End point of building travel. Buy from shop
				if World.get_world().buildings[self.building_id].type == Building.TYPE_CLOTHES:
					# in a clothes store, get random clothes
					if self.am_incharge():
						self.random_outfit()
						self.update_remote_state()

					if self.is_active_player():
						CASH_SOUND.play()

				elif World.get_world().buildings[self.building_id].type == Building.TYPE_BOMB:
					# in a bomb store
					if self.has_bomb == False and self.bomb_location == None:
						# purchase a bomb
#						print "Picked up a bomb"
						self.has_bomb = True
						CASH_SOUND.play()
			if self.building_cooldown < 0:
#				print "finished in building, moving on"
				self.is_in_building = False
				player = self.get_player()
				DOOR_CLOSE_SOUND.play()
				if player != None and player.mission == Player.MISSION_BUILDING \
						and player.mission_target == self.building_id:
					# player has completed a mission in a building
					player.complete_mission()

				return
			return
		if self.stopped:
			return

		self.movement_update_helper(time)

		if self.location < PATH_INTERSECTS[0]:
			self.location = PATH_INTERSECTS[0]
		elif self.location > PATH_INTERSECTS[7]:
			self.location = PATH_INTERSECTS[7]

#		if left_right_path(self.path) != (self.direction == LEFT or self.direction == RIGHT):
#			print "Wargh direction set wrong"


from net import broadcast_dude_update, broadcast_die
from net import broadcast_hint

