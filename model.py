import random
from pyglet import *
import math
import anim
from map import *

LEFT, RIGHT, UP, DOWN = range(4)

BLUE, YELLOW, GREEN = range(3)
HAT, NO_HAT = range(2)

MISSION_ASSIGN_SOUND = resource.media('assets/Mission Assigned.wav', streaming=False)
MISSION_WIN_SOUND = resource.media('assets/Mission Complete.wav', streaming=False)

class Player(object):
	FLAG_SOVIET, FLAG_UK, FLAG_US, FLAG_GERM = range(4)

	FLAG_ICONS = {FLAG_SOVIET: image.load('assets/New Hud/Flags/sov_flag_w.png'),
			FLAG_UK: image.load('assets/New Hud/Flags/uk_flag_w.png'),
			FLAG_US: image.load('assets/New Hud/Flags/us_flag_w.png'),
			FLAG_GERM: image.load('assets/New Hud/Flags/e_germ_flag_w.png')}

	MISSION_BUILDING = 0
	MISSION_ICONS = {MISSION_BUILDING: image.load('assets/New Hud/Mission_Icons/miss_enter_bldg.png'),
			}

	DUDE_OUTFITS = {
		(HAT, BLUE):      image.load('assets/New Hud/Photos/blue_hat.png'),
		(NO_HAT, BLUE):   image.load('assets/New Hud/Photos/blue_no_hat.png'),
		(HAT, YELLOW):    image.load('assets/New Hud/Photos/yellow_hat.png'),
		(NO_HAT, YELLOW): image.load('assets/New Hud/Photos/yellow_no_hat.png'),
		(HAT, GREEN):     image.load('assets/New Hud/Photos/green_hat.png'),
		(NO_HAT, GREEN):  image.load('assets/New Hud/Photos/green_no_hat.png'),
	}

	BOMB_ICONS = (image.load('assets/Lower Hud/bomb_icon_grey.png'),
			image.load('assets/Lower Hud/bomb_icon_black.png'))

	SHOT = image.load('assets/Lower Hud/gun_icon_black.png')
	player_border = image.load('assets/New Hud/player_hud_border.png')

	frame = image.load('assets/Lower Hud/lower_hud_frame.png')

	background = image.load('assets/New Hud/hud_background.png')

	skull = image.load('assets/New Hud/death_marker.png')

	def __init__(self, id, state = None):
		self.id = id
		self.mission = None
		self.mission_target = None
		self.mission_cooldown = 5.0
		self.hint_cooldown = random.random()*10 + 5

		self.name = {0:"n1k1ta_k", 1:"JBJ_007", 2:"Felix_L", 3:"Stazi_M"}[id]

		self.batch = graphics.Batch()

		self.name_label = text.Label(text = self.name, batch = self.batch,\
				font_name="Courier New", font_size=12, bold=True,\
				color=(0,0,0,255), halign='center',\
				x = 5, y = self.get_offset_y() + 104, width = 140, height = 40)

		self.score_label = text.Label(batch = self.batch,\
				font_name="Courier New", font_size=18, bold=True,\
				color=(0,0,0,255), halign='right',\
				x = 6, y = self.get_offset_y() + 13, width = 103, height = 40)

		self.death_count_label = text.Label(batch = self.batch,\
				font_name="Courier New", font_size=18, bold=True,\
				color=(0,0,0,255), halign='center',\
				x = 24, y = self.get_offset_y() + 76, width = 84, height = 26)

		self.death_count = 0
		self.score = 0

		self.appearance = None

		self.mission_sprite = None
		self.mission_target_sprite = None

		if state != None:
			self.set_state(state)

		offset_y = self.get_offset_y()

		self.flag = sprite.Sprite(self.FLAG_ICONS[self.id], batch=self.batch,
				x = 6, y = offset_y + 180 - 57)

		self.background_sprite = sprite.Sprite(self.background, x = 0, y = offset_y)

		self.reveal_appearance = 0
		self.reveal_mission = 0
		self.skull_sprite = None

#		if World.my_player_id == self.id:
		self.player_border_sprite = sprite.Sprite(self.player_border, x = 0, y = self.get_offset_y())
		self.bomb_sprite = sprite.Sprite(self.BOMB_ICONS[1], x=0, y=0)
		self.shot_sprite = sprite.Sprite(self.SHOT, x=208, y=0)

	def get_state(self):
		return (self.id, self.mission, self.mission_target, self.mission_cooldown,\
				self.name, self.death_count, self.score)

	def set_state(self, state):
#		print "player setstate", state
		oldmission = self.mission
		oldmission_target = self.mission_target

		(id, self.mission, self.mission_target, self.mission_cooldown,\
				self.name, self.death_count, self.score) = state

		if oldmission != self.mission or oldmission_target != self.mission_target:
			if self.mission != None and self.id == World.my_player_id:
				if not World.mute: MISSION_ASSIGN_SOUND.play()

			self.clear_mission_sprites()
	
	def update_dude_sprites(self):
		if (self.appearance != None):
			self.appearance.delete()
			self.appearance = None

		dude = self.get_dude()

		offset_y = self.get_offset_y()

		self.appearance = sprite.Sprite(self.DUDE_OUTFITS[(dude.outfit, dude.colour)], batch=self.batch,
				x = 147, y = offset_y + 86)

	def clear_mission_sprites(self):
		if (self.mission_sprite != None):
			self.mission_sprite.delete()
			self.mission_sprite = None

		if (self.mission_target_sprite != None):
			self.mission_target_sprite.delete()
			self.mission_target_sprite = None


	def update_mission_sprites(self):
		self.clear_mission_sprites()

		if self.mission != None:
			offset_y = self.get_offset_y()

			self.mission_sprite = sprite.Sprite(self.MISSION_ICONS[self.mission],
					batch = self.batch, x = 112, y = offset_y + 9)

			target_building = World.get_world().buildings[self.mission_target]

			self.mission_target_sprite = sprite.Sprite(\
					Building.BUILDING_TYPE[target_building.type][2],
					batch = self.batch, x = 182, y = offset_y + 9)

	def getscore(self):
		return self._score

	def setscore(self, value):
		self._score = value
		self.score_label.text = str(value * 1000)

	def increment_score(self, inc=1):
		if self.score + inc < 0:
			inc = -self.score
		self.score += inc
		self.update_remote_state()

	score = property(getscore, setscore)

	def get_deaths(self):
		return self._death_count

	def set_deaths(self, value):
		self._death_count = value
		self.death_count_label.text = str(value)

	death_count = property(get_deaths, set_deaths)

	def update(self, time):
		if self.appearance == None:
			self.update_dude_sprites()

		if self.mission_sprite == None and self.mission != None:
			self.update_mission_sprites()

		if World.is_server:
			self.mission_cooldown -= time
			if self.mission_cooldown <= 0.0 and self.mission == None:
				# no mission and cooldown's up, get a new mission
				self.mission = self.MISSION_BUILDING
				self.mission_target = random.choice(range(16))
				self.update_mission_sprites()
				self.update_remote_state()
				if self.id == World.my_player_id:
					if not World.mute: MISSION_ASSIGN_SOUND.play()

			self.hint_cooldown -= time
			if self.hint_cooldown <= 0.0:
				if random.random() < 0.5:
					net.my_peer.broadcast_hint(self.id, 'appearance')
				else:
					net.my_peer.broadcast_hint(self.id, 'mission')

				self.hint_cooldown = random.random() * 10 + 7

		if self.mission_sprite and not (self.reveal_mission > 0 or self.id == World.my_player_id):
			self.mission_sprite.visible = False
			self.mission_target_sprite.visible = False
		else:
			if self.mission_sprite:
				self.mission_sprite.visible = True
				self.mission_target_sprite.visible = True
		if not (self.reveal_appearance > 0 or self.id == World.my_player_id):
			if self.appearance:
				self.appearance.visible = False
		else:
			if self.appearance:
				self.appearance.visible = True

		self.reveal_mission -= time
		self.reveal_appearance -= time

	def update_remote_state(self):
		net.my_peer.broadcast_player_update(self.get_state())

	def get_dude(self):
		return World.get_world().dudes[self.id]

	def get_offset_y(self):
		return 768 - ((self.id + 1) * 180)

	def draw_hud(self):
		self.background_sprite.draw()

		self.batch.draw()

		if not self.get_dude().alive:
			if self.skull_sprite == None:
				self.skull_sprite = sprite.Sprite(self.skull, 0, self.get_offset_y())

			self.skull_sprite.draw()
		elif self.get_dude().alive and self.skull_sprite != None:
			self.skull_sprite.delete()
			self.skull_sprite = None

		if World.my_player_id == self.id:
			self.frame.blit(0, 0)

			if self.get_dude().has_bomb:
				self.bomb_sprite.draw()

			if self.get_dude().shot_cooldown <= 0:
				self.shot_sprite.draw()
		
			self.player_border_sprite.draw()

	def complete_mission(self):
		print "Player ", self.id, " has completed a mission"
		if not World.mute: MISSION_WIN_SOUND.play()
		self.score += 1
		self.mission = None
		self.mission_cooldown = 7.0
		self.update_mission_sprites()

	def mission_target_bombed(self):
		self.mission = None
		self.mission_cooldown = 7.


COLOUR_RED, COLOUR_BLUE, COLOUR_GREEN = range(3)
LAUGH1_SOUND = resource.media('assets/Manic Laugh.wav', streaming=False)
LAUGH2_SOUND = resource.media('assets/Evil Laugh.wav', streaming=False)

class World:
	is_server = True
	batch = None

	def __init__(self, state = None):
		World.batch = graphics.Batch()
		self.buildings = []
		self.dudes = []
		self.background = image.load('assets/city_all.png')
		self.hud_mockup = image.load('assets/hud_mockup.png')
		self.doors = []
		self.map = Map()

		self.win = sprite.Sprite(image.load('assets/compl.png'), batch=World.batch, group=anim.OVERLAY)
		self.win.x = 256
		self.win.y = 0
		self.win.visible = False
		self.lose = sprite.Sprite(image.load('assets/failed.png'), batch=World.batch, group=anim.OVERLAY)
		self.lose.x = 256
		self.lose.y = 0
		self.lose.visible = False

		self.connected = True

		crosshair = image.load('assets/crosshair_2.png')
		crosshair.anchor_x = crosshair.width // 2
		crosshair.anchor_y = crosshair.height // 2
		self.crosshair = sprite.Sprite(crosshair, batch=World.batch)

		self.players = [None, None, None, None]

		if state is None:
			# init
			building_types = range(16)
			random.shuffle(building_types)
			for i in xrange(16):
				building = Building(i, type=building_types[i])
				self.buildings.append(building)
				self.map.add_node(building) # XXX hack... buildings must be the first 16 nodes

			self.create_paths()

			for i in xrange(20):
				self.add_dude()

			World.my_player_id = self.allocate_new_playerid(suppress_update=True)
		else:
			# construct from given state
			(building_state, dude_state, player_state) = state

			for i in xrange(len(building_state)):
				building = Building(i, state=building_state[i])
				self.buildings.append(building)
				self.map.add_node(building)

			self.create_paths()

			self.dudes = [Dude(self, state=s) for s in dude_state]

			self.set_players_state(player_state)


	__instance = None
	@classmethod
	def get_world(cls):
		return cls.__instance

	@classmethod
	def set_world(cls, world):
		cls.__instance = world

	# |  |         |  |   |
	# |  |<--104-->|28|   |
	# |  +---------+  |42 |
	# |    28         |   |
	# +---------------+---+---
	#  <-------202------->
	def create_paths(self):
		BL, TL, TR, BR = range(4)
		building_nodes = {}
		for yb in xrange(4):
			for xb in xrange(4):
				b_nodes = [
						Node(1 + 14+xb*202, 1 + 14+yb*202), # bottom-left
						Node(1 + 14+xb*202, 1 + 28+104+14+yb*202), # top-left
						Node(1 + 28+104+14+xb*202, 1 + 28+104+14+yb*202), # top-right
						Node(1 + 28+104+14+xb*202, 1 + 14+yb*202), # bottom-right
					]

				for n in b_nodes:
					self.map.add_node(n)

				building_nodes[xb,yb] = b_nodes

		for yb in xrange(4):
			for xb in xrange(4):
				bnodes = building_nodes[xb,yb]

				# link internally
				bnodes[BL].edges[UP]    = bnodes[TL]
				bnodes[TL].edges[DOWN]  = bnodes[BL]
				bnodes[TL].edges[RIGHT] = bnodes[TR]
				bnodes[TR].edges[LEFT]  = bnodes[TL]
				bnodes[TR].edges[DOWN]  = bnodes[BR]
				bnodes[BR].edges[UP]    = bnodes[TR]
				bnodes[BR].edges[LEFT]  = bnodes[BL]
				bnodes[BL].edges[RIGHT] = bnodes[BR]

				if xb < 3:
					# link to the right
					other_bnodes = building_nodes[xb+1,yb]
					bnodes[TR].edges[RIGHT] = other_bnodes[TL]
					bnodes[BR].edges[RIGHT] = other_bnodes[BL]
				if xb > 0:
					# link to the left
					other_bnodes = building_nodes[xb-1,yb]
					bnodes[TL].edges[LEFT] = other_bnodes[TR]
					bnodes[BL].edges[LEFT] = other_bnodes[BR]

				if yb < 3:
					# link up
					other_bnodes = building_nodes[xb,yb+1]
					bnodes[TL].edges[UP] = other_bnodes[BL]
					bnodes[TR].edges[UP] = other_bnodes[BR]
				if yb > 0:
					# link down
					other_bnodes = building_nodes[xb,yb-1]
					bnodes[BL].edges[DOWN] = other_bnodes[TL]
					bnodes[BR].edges[DOWN] = other_bnodes[TR]

		for b in self.buildings:
			xb, yb = b.id % 4, b.id / 4
			side, dist = Building.BUILDING_TYPE[b.type][1] # (UP, 0.5) = top side, half way

			door_node = Node(0,0)
			self.map.add_node(door_node)
			bnodes = building_nodes[xb,yb]

			if side == UP:
				door_node.x = 1 + xb*202 + 28 + 104 * dist
				door_node.y = 1 + yb*202 + 28 + 104 + 14
				door_node.edges[LEFT]  = bnodes[TL]
				door_node.edges[RIGHT] = bnodes[TR]
				bnodes[TL].edges[RIGHT] = door_node
				bnodes[TR].edges[LEFT]  = door_node
				door_node.edges[DOWN] = b
				b.edges[UP] = door_node
			elif side == DOWN:
				door_node.x = 1 + xb*202 + 28 + 104 * dist
				door_node.y = 1 + yb*202 + 14
				door_node.edges[LEFT]  = bnodes[BL]
				door_node.edges[RIGHT] = bnodes[BR]
				bnodes[BL].edges[RIGHT] = door_node
				bnodes[BR].edges[LEFT]  = door_node
				door_node.edges[UP] = b
				b.edges[DOWN] = door_node
			elif side == LEFT:
				door_node.x = 1 + xb*202 + 14
				door_node.y = 1 + yb*202 + 28 + 104 * dist
				door_node.edges[UP]   = bnodes[TL]
				door_node.edges[DOWN] = bnodes[BL]
				bnodes[TL].edges[DOWN] = door_node
				bnodes[BL].edges[UP]   = door_node
				door_node.edges[RIGHT] = b
				b.edges[LEFT] = door_node
			elif side == RIGHT:
				door_node.x = 1 + xb*202 + 28 + 104 + 14
				door_node.y = 1 + yb*202 + 28 + 104 * dist
				door_node.edges[UP]   = bnodes[TR]
				door_node.edges[DOWN] = bnodes[BR]
				bnodes[TR].edges[DOWN] = door_node
				bnodes[BR].edges[UP]   = door_node
				door_node.edges[LEFT] = b
				b.edges[RIGHT] = door_node

	def allocate_new_playerid(self, suppress_update=False):
		if not None in self.players:
			return None

		player_id = self.players.index(None)

		if player_id > len(self.dudes):
			print "No dudes to take control of!"
			return None

		self.players[player_id] = Player(player_id)
		self.dudes[player_id].take_control_by(player_id, suppress_update)

		if not suppress_update:
			self.broadcast_all_player_state()

		return player_id

	def drop_player(self, player_id):
		self.players[player_id] = None
		self.dudes[player_id].take_control_by(None, suppress_update=True)
		if World.is_server:
			net.my_peer.broadcast_player_dropped(player_id)

	def broadcast_all_player_state(self):
		for player_state in self.get_player_state():
			if player_state is None: continue
			net.my_peer.broadcast_player_update(player_state)


	def add_dude(self):
		d = Dude(self, id = len(self.dudes))
		d.randomise(suppress_update=True)
		self.dudes.append(d)

	def nearest_dude_to(self, dude):
		if dude.is_in_building(): return None
		x1, y1 = dude.xy()
		mindist = None
		nearestDude = None
		for d in self.dudes:
			if d is dude: continue
			if not d.alive: continue
			if d.is_in_building(): continue
			x2, y2 = d.xy()
			dy = y2 - y1
			dx = x2 - x1
			dist = math.sqrt(dy*dy + dx*dx)
			if dist < 100 and (mindist is None or dist < mindist):
				mindist = dist
				nearestDude = d

		return nearestDude

	def get_player_dude(self, player_id):
		return self.dudes[player_id]
		
	def is_over(self):
		return any([p and p.score >= 7 for p in self.players]) or not self.connected

	def draw(self, window):
		# background
		self.background.blit(256,0)

		self.draw_hud()

		if self.is_over():
			if self.players[World.my_player_id].score >= 7:
				self.win.visible = True
			else:
				self.lose.visible = True

		for d in self.dudes:
			d.draw(window)

		for b in self.buildings:
			b.draw(window)

		player = self.get_player_dude(World.my_player_id)
		nearest = self.nearest_dude_to(player)
		if nearest:
			xy = nearest.xy()
			self.crosshair.set_position(256 + 1 + xy[0], 1 + xy[1])
			self.crosshair.visible = True
		else:
			self.crosshair.visible = False

		World.batch.draw()

		# hud
#		label = text.Label("FPS: %d" % clock.get_fps(), font_name="Georgia",
#				font_size=24, x=0, y=7)
#		label.draw()

	def draw_hud(self):
		for p in self.players:
			if p != None:
				p.draw_hud()

	def update(self, time):
		if self.is_over(): return

		for b in self.buildings:
			b.update(time)

		for d in self.dudes:
			d.update(time)
			
		for p in self.players:
			if p != None:
				p.update(time)

	def get_player_state(self):
		return [p and p.get_state() or None for p in self.players]

	def set_players_state(self, players):
		for s in players:
			self.set_player_state(s)
	
	def set_player_state(self, player_state):
		if player_state == None:
			return

		id = player_state[0]

		if player_state != None and self.players[id] == None:
			self.players[id] = Player(id = id, state = player_state)
#		elif player_state == None and self.players[i] != None:
#			self.players[id] = None
		elif player_state != None and self.players[id] != None:
			self.players[id].set_state(player_state)



	# For net sync
	def state(self):
		return ([b.state() for b in self.buildings],
				[d.state() for d in self.dudes],
				self.get_player_state())

	def update_dude(self, dude_state):
		self.dudes[dude_state[0]].update_local_state(dude_state)

	def remote_explode(self, state):
		terrorist_id, building_id = state
		(x,y) = self.dudes[terrorist_id].xy()
		(myx, myy) = self.dudes[self.my_player_id].xy()
		d = math.sqrt((x-myx)*(x-myx) + (y-myy)*(y-myy))
		if d < 100:
			laugh = random.choice([LAUGH1_SOUND, LAUGH2_SOUND])

		self.buildings[building_id].explode(terrorist_id, suppressBroadcast=True)

class Building(Node):
	TYPE_CLOTHES, TYPE_BOMB, TYPE_HOSPITAL, TYPE_MUSEUM,\
	TYPE_DISCO, TYPE_ARCADE, TYPE_CARPARK, TYPE_FACTORY,\
	TYPE_OFFICE, TYPE_PARK, TYPE_WAREHOUSE, TYPE_BANK,\
	TYPE_RESTAURANT, TYPE_TOWNHALL, TYPE_RADIO, TYPE_CHURCH = range(16)
	
	BOMB_SOUND = resource.media('assets/Bomb Detonation.wav', streaming=False)
	DEATH_SCREAM = resource.media('assets/Death Scream.wav', streaming=False)
	CIV_SCREAM = resource.media('assets/Scream 1.wav', streaming=False)

	RUBBLE = image.load('assets/Building_assets/rubble_fin.png')
	RUBBLE.anchor_x = RUBBLE.width // 2
	RUBBLE.anchor_y = RUBBLE.height // 2

	BUILDING_TYPE = {
			TYPE_CLOTHES: (image.load('assets/Building_assets/clothes_test.png'), (DOWN, 0.5),
				image.load('assets/New Hud/Building_Stamps/clothes_icon.png')),
			TYPE_BOMB: (image.load('assets/Building_assets/bomb_test.png'), (RIGHT, 0.78),
				image.load('assets/New Hud/Building_Stamps/bomb_icon.png')),
			TYPE_HOSPITAL: (image.load('assets/Building_assets/hospital_test.png'), (UP, 0.5),
				image.load('assets/New Hud/Building_Stamps/hospital_icon.png')),
			TYPE_MUSEUM: (image.load('assets/Building_assets/museum_test.png'), (DOWN, 0.5),
				image.load('assets/New Hud/Building_Stamps/museum_icon.png')),
			TYPE_DISCO: (anim.load_anim('Building_assets/Disco_Anim', fps=2), (DOWN, 0.5),
				image.load('assets/New Hud/Building_Stamps/club_icon.png')),
			TYPE_ARCADE: (image.load('assets/Building_assets/arcade_test.png'), (LEFT, 0.5),
				image.load('assets/New Hud/Building_Stamps/arcade_icon.png')),
			TYPE_CARPARK: (image.load('assets/Building_assets/carpark_test.png'), (UP, 0.5),
				image.load('assets/New Hud/Building_Stamps/parking_icon.png')),
			TYPE_FACTORY: (anim.load_anim('Building_assets/Factory_anim', fps=7), (RIGHT, 0.3),
				image.load('assets/New Hud/Building_Stamps/factory_icon.png')),
			TYPE_OFFICE: (anim.load_anim('Building_assets/Office_anim', fps=1), (UP, 0.5),
				image.load('assets/New Hud/Building_Stamps/office_icon.png')),
			TYPE_PARK: (anim.load_anim('Building_assets/Park_Anim', fps=2), (UP, 0.5),
				image.load('assets/New Hud/Building_Stamps/park_icon.png')),
			TYPE_WAREHOUSE: (image.load('assets/Building_assets/warehouse_test.png'), (DOWN, 0.5),
				image.load('assets/New Hud/Building_Stamps/warehouse_icon.png')),
			TYPE_BANK: (image.load('assets/Building_assets/bank_test.png'), (DOWN, 0.5),
				image.load('assets/New Hud/Building_Stamps/bank_icon.png')),
			TYPE_RESTAURANT: (image.load('assets/Building_assets/cafe_test.png'), (UP, 0.3),
				image.load('assets/New Hud/Building_Stamps/cafe_icon.png')),
			TYPE_TOWNHALL: (anim.load_anim('Building_assets/Hall_anim', fps=8), (DOWN, 0.5),
				image.load('assets/New Hud/Building_Stamps/city_hall_icon.png')),
			TYPE_RADIO: (anim.load_anim('Building_assets/Radio_anim', fps=2), (DOWN, 0.7),
				image.load('assets/New Hud/Building_Stamps/radio_icon.png')),
			TYPE_CHURCH: (image.load('assets/Building_assets/church_test.png'), (LEFT, 0.5),
				image.load('assets/New Hud/Building_Stamps/church_icon.png')),
			}

	for k in BUILDING_TYPE:
		v = BUILDING_TYPE[k]
		if isinstance(v[0], image.AbstractImage):
			v[0].anchor_x = v[0].width // 2
			v[0].anchor_y = v[0].height // 2

	EXPLOSION = anim.load_anim('Explosion', loop=False)
	DOOR_LIGHT = image.load('assets/light_beam.png')

	def __init__(self, id, type=None, state=None):
		x = 1 + 28 + 202 * (id % 4) + 104/2
		y = 1 + 28 + 202 * (id / 4) + 104/2
		Node.__init__(self, x, y)

		self.id = id
		self.type = type
		self.has_bomb = False
		self.blownup_cooldown = 0

		if state != None:
			(self.type, self.has_bomb, self.blownup_cooldown) = state

		self.sprite = sprite.Sprite(self.BUILDING_TYPE[self.type][0],
				group=anim.ROOF, batch=World.batch)
		self.sprite.x = 256 + x
		self.sprite.y = y

		self.rubble = sprite.Sprite(self.RUBBLE, group=anim.ROOF, batch=World.batch)
		self.rubble.x = 256 + x
		self.rubble.y = y
		self.rubble.visible = False

		self.light = sprite.Sprite(self.DOOR_LIGHT, group=anim.PATH,
				batch=World.batch)
		door_loc = self.BUILDING_TYPE[self.type][1]

		bx = 256 + 1 + 28 + 202 * (id % 4)
		by = 1 + 28 + 202 * (id / 4)

		# now we set location on the side
		if door_loc[0] == LEFT:
			self.light.rotation = -90
			self.light.x = bx
			self.light.y = by + door_loc[1] * 104 - self.light.image.width // 2
		elif door_loc[0] == RIGHT:
			self.light.rotation = 90
			self.light.x = bx + 104
			self.light.y = by + door_loc[1] * 104 + self.light.image.width // 2
		elif door_loc[0] == DOWN:
			self.light.rotation = 180
			self.light.x = bx + door_loc[1] * 104 + self.light.image.width // 2
			self.light.y = by
		elif door_loc[0] == UP:
			self.light.rotation = 0
			self.light.x = bx + door_loc[1] * 104 - self.light.image.width // 2
			self.light.y = by + 104

		self.explosion_sprite = None
		self.exploding = False

		self.destroyed = None
	
	def draw(self, window):
		#self.light.draw()
		#self.sprite.draw()
		#if self.explosion_sprite:
			#self.explosion_sprite.draw()
		pass

	def update(self, time):
		if self.destroyed != None:
			self.destroyed -= time
			if self.destroyed < 0:
				self.destroyed = None
				self.sprite.visible = True
				self.light.visible = True
				self.rubble.visible = False

	def screen_coords(self):
		return (256 + self.x, self.y)

	def explode(self, terrorist_id, suppressBroadcast=False):
		if self.exploding: return
		
		print "exploding!"
		
		if not suppressBroadcast:
			net.my_peer.broadcast_building_explosion((World.my_player_id, self.id))

		if not World.mute: self.BOMB_SOUND.play()
		self.exploding = True
		def explosion_animation(dt):
			self.explosion_sprite = sprite.Sprite(self.EXPLOSION, group=anim.SKY,
					batch=World.batch)
			self.explosion_sprite.x, self.explosion_sprite.y = self.screen_coords()

			self.destroyed = 15
			self.sprite.visible = False
			self.light.visible = False
			self.rubble.visible = True

			terrorist = World.get_world().players[terrorist_id]

			for player in World.get_world().players:
				if player == None:
					continue

				if player.mission_target == self.id:
					# bomb has destroyed a mission, wipe mission for no points
					player.mission_target_bombed()

			killed_civ = False
			killed_player = False
			for dude in World.get_world().dudes:
				if dude.building_id() == self.id:
					# a dude has been caught inside the bomb blast
					if World.is_server:
						terrorist.get_dude().kill(dude)
					if dude.player_id == None:
						killed_civ = True
						if not World.mute: self.CIV_SCREAM.play()
					else:
						if dude.id != terrorist_id:
							killed_player = True
						if not World.mute: self.DEATH_SCREAM.play()

			if killed_civ and not killed_player:
				# Killed an innocent without a player . . . broadcast a hint about this player
				if random.random() < 0.5:
					net.my_peer.broadcast_hint(terrorist.id, 'appearance')
				else:
					net.my_peer.broadcast_hint(terrorist.id, 'mission')

			@self.explosion_sprite.event
			def on_animation_end():
				del self.explosion_sprite
				self.explosion_sprite = None
				self.exploding = False

		clock.schedule_once(explosion_animation, 0.6)

	def state(self):
		return (self.type, self.has_bomb, self.blownup_cooldown)

from Dude import *
import net
