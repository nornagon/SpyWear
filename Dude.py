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
	STRAIGHT_MARKER = image.load('assets/straight_arrow.png')
	STRAIGHT_MARKER.anchor_x = STRAIGHT_MARKER.width // 2
	STRAIGHT_MARKER.anchor_y = STRAIGHT_MARKER.height // 2

	# dude speed in pixels/sec
	SPEED = 50.0

	def reset(self):
		self.node = self.world.map.nodes[0]
		self.direction = self.node.edges.keys()[0]
		self.distance = 0.0
		self.workout_next_direction(suppress_update=True)
		self.outfit = HAT
		self.colour = BLUE

		self.shot_cooldown = 0.0
		
		self.has_bomb = False
		#self.has_bomb = True
		self.bomb_location = None

		self.alive = True
		self.fading = False

		self.idle_time = 0.0

		self.time_to_enter = random.random() * 20 + 3

	def __init__(self, world, id=None, state=None):
		self.world = world
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

	def state(self):
		return (self.id, self.node.id, self.distance, self.direction,
				self.next_direction, self.outfit, self.colour,
				self.has_bomb, self.bomb_location, self.player_id,
				self.alive)

	def update_local_state(self, remotestate):
		old_alive = self.alive
		old_outfit = self.outfit
		old_colour = self.colour

		(id, node_id, self.distance, self.direction,
				self.next_direction, self.outfit, self.colour,
				self.has_bomb, self.bomb_location, self.player_id,
				self.alive) = remotestate

		self.node = self.world.map.nodes[node_id]

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
		self.node = self.world.buildings[building_id]
		self.direction = self.node.edges.keys()[0]
		self.distance = 0.0
		self.next_direction = self.next_node().edges.keys()[0] # TODO: random

		self.random_outfit(suppress_update = True)
		self.update_remote_state()

	def xy(self):
		return self.node.pointAt(self.direction, self.distance)

	def reset_idle_timer(self):
		self.idle_time = 20.0
	
	def take_control_by(self, player_id, suppress_update=False):
		self.player_id = player_id
		self.idle_time = 0.0
		if not suppress_update:
			self.update_remote_state()

	def update_remote_state(self):
		net.my_peer.broadcast_dude_update(self.state())

	def is_active_player(self):
		return World.my_player_id == self.id

	def am_incharge(self):
		return self.is_active_player() or (World.is_server and self.player_id == None)

	def set_sprite(self, spr):
		if self.sprite:
			self.sprite.delete()
		self.sprite = spr
		self.sprite.visible = True

	def randomise(self, suppress_update=False):
		self.node = random.choice(self.world.map.nodes)
		self.direction = random.choice(self.node.edges.keys())
		self.distance = random.random() * self.node.distanceTo(self.direction)
		self.outfit = random.choice([HAT, NO_HAT])
		self.colour = random.choice([BLUE, YELLOW, GREEN])

		self.set_sprite(sprite.Sprite(self.DUDE_OUTFITS[(self.outfit,self.colour)],
				batch=World.batch, group=anim.GROUND))

		self.workout_next_direction(suppress_update=True)

		if not suppress_update:
			self.update_remote_state()

	def draw(self, window):
		if not self.marker and self.is_active_player():
			self.marker = sprite.Sprite(self.DUDE_MARKER, batch=World.batch,
					group=anim.MARKER)
			self.turn_marker = sprite.Sprite(self.TURN_MARKER, batch=World.batch, group=anim.PATH)
			self.turn_marker.visible = False
			self.turn_marker_flip = sprite.Sprite(self.TURN_MARKER_FLIP, batch=World.batch, group=anim.PATH)
			self.turn_marker_flip.visible = False
			self.straight_marker = sprite.Sprite(self.STRAIGHT_MARKER, batch=World.batch, group=anim.PATH)
			self.straight_marker.visible = False


		if self.direction == LEFT:
			self.sprite.rotation = -90
		elif self.direction == RIGHT:
			self.sprite.rotation = 90
		elif self.direction == UP:
			self.sprite.rotation = 0
		elif self.direction == DOWN:
			self.sprite.rotation = 180

		xy = self.xy()
		self.sprite.x = 256 + xy[0]
		self.sprite.y = xy[1]

		if self.marker:
			self.marker.rotation = self.sprite.rotation
			self.marker.x = self.sprite.x
			self.marker.y = self.sprite.y

			if self.next_direction != None and not isinstance(self.next_node(), Building):
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
				elif self.direction == self.next_direction or \
						self.direction == self.opposite(self.next_direction):
					m = self.straight_marker
					if self.next_direction == LEFT:
						m.rotation = -90
					elif self.next_direction == RIGHT:
						m.rotation = 90
					elif self.next_direction == UP:
						m.rotation = 0
					elif self.next_direction == DOWN:
						m.rotation = 180

				for b in [self.turn_marker, self.turn_marker_flip, self.straight_marker]:
					if m is b:
						b.visible = True
					else:
						b.visible = False

				n = self.next_node()
				m.x = 256 + n.x
				m.y = n.y
			else:
				self.turn_marker.visible = False
				self.turn_marker_flip.visible = False

	def next_node(self):
		return self.node.edges[self.direction]

	def turn(self, new_direction):
		if not isinstance(self.next_node(), Building):
			if new_direction in self.valid_next_directions():
				self.next_direction = new_direction
				self.update_remote_state()
 
	def building_id(self):
		if isinstance(self.node, Building):
			return self.node.id
		elif isinstance(self.next_node(), Building):
			return self.next_node().id
		else:
			return None

	def is_in_building(self):
		return self.building_id() != None

	def bomb(self):
		# if in building, set bomb
		if self.is_in_building() and self.has_bomb:
			self.bomb_location = self.building_id()
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
			if not World.mute: ARM_BOMB_SOUND.play()
		
		# if bomb in play, set off bomb
		elif self.bomb_location != None and self.alive:
			World.get_world().buildings[self.bomb_location].explode(self.id)
			self.has_bomb = False
			if not (self.is_in_building() and self.building_id == self.bomb_location):
				laugh = random.choice([LAUGH1_SOUND, LAUGH2_SOUND])
				if not World.mute: clock.schedule_once(lambda dt: laugh.play(), 1.0)
			self.bomb_location = None

	def shoot(self):
		if self.shot_cooldown > 0 or not self.alive: return
		dead_guy = World.get_world().nearest_dude_to(self)
		if not dead_guy: return
		net.my_peer.broadcast_die(World.my_player_id, dead_guy.id)
		dead_guy.die()
		if not World.mute: KILL_SOUND.play()
		if dead_guy.player_id == None:
			# Killed a Civilian, send out hint about player
			if random.random() < 0.5:
				net.my_peer.broadcast_hint(self.id, 'appearance')
			else:
				net.my_peer.broadcast_hint(self.id, 'mission')
		else:
			# Killed a Player
			self.get_player().increment_score(1)
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

	def random_outfit(self, suppress_update = False):
		self.outfit = random.choice([HAT, NO_HAT])

		colours = [BLUE, YELLOW, GREEN]
		colours.remove(self.colour)
		self.colour = random.choice(colours)
		self.update_sprite()
#		print "Changed clothes to ", self.outfit, self.colour

		if (self.player_id != None):
			self.get_player().update_dude_sprites()

		if not suppress_update:
			self.update_remote_state()

	def valid_next_directions(self):
		dirs = self.next_node().edges.keys()
		if isinstance(self.node, Building):
			dirs.remove(self.opposite(self.direction))
		for d in dirs:
			e = self.next_node().edges[d]
			if isinstance(e, Building) and e.destroyed:
				dirs.remove(d)
		return dirs

	def workout_next_direction(self, suppress_update=False):
		directions = self.valid_next_directions()
		self.next_direction = random.choice(directions)
		if not suppress_update:
			self.update_remote_state()

	def entering_node(self, node):
		if isinstance(node, Building):
			if node.type == Building.TYPE_CLOTHES:
				# in a clothes store, get random clothes
				if self.am_incharge():
					self.random_outfit()

				if self.is_active_player():
					if not World.mute: CASH_SOUND.play()

			elif node.type == Building.TYPE_BOMB:
				# in a bomb store
				if self.has_bomb == False and self.bomb_location == None:
					# purchase a bomb
					self.has_bomb = True
					if not World.mute: CASH_SOUND.play()
		else:
			# not entering a building
			if isinstance(self.node, Building):
				# but currently inside one
				if not World.mute: DOOR_CLOSE_SOUND.play().volume = 0.4
				player = self.get_player()
				if player != None and player.mission == Player.MISSION_BUILDING \
						and player.mission_target == self.node.id:
					# player has completed a mission in a building
					player.complete_mission()

	def changed_node(self):
		if isinstance(self.next_node(), Building):
			if not World.mute: DOOR_OPEN_SOUND.play().volume = 0.4

	# do movement update.
	def movement_update_helper(self, time):
		if not self.next_direction in self.valid_next_directions():
			self.workout_next_direction() # uhhhh... someone lagged out :/

		frame_distance = time * self.SPEED
		self.distance += frame_distance
		distance_to_next_node = self.node.distanceTo(self.direction)
		if self.distance >= distance_to_next_node:
			self.entering_node(self.next_node())

			self.node = self.next_node()
			self.direction = self.next_direction
			self.distance -= distance_to_next_node
			if (self.player_id is None and World.is_server) or \
					(self.is_active_player() and (self.idle_time <= 0 or \
						(not self.next_direction in self.valid_next_directions()))):
				self.workout_next_direction()
			self.changed_node()

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

		self.idle_time -= time
		if self.idle_time < 0: self.idle_time = 0

		self.shot_cooldown -= time
		if self.shot_cooldown < 0: self.shot_cooldown = 0

		self.movement_update_helper(time)

import net
