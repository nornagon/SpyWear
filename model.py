import random
from pyglet import *
import math
import anim

BLUE, YELLOW, GREEN = range(3)
HAT, NO_HAT = range(2)

class Player(object):
	FLAG_SOVIET, FLAG_UK, FLAG_US, FLAG_GERM = range(4)

	FLAG_ICONS = {FLAG_SOVIET: image.load('assets/Hud/Flags/sov_flag_w.png'),
			FLAG_UK: image.load('assets/Hud/Flags/uk_flag_w.png'),
			FLAG_US: image.load('assets/Hud/Flags/us_flag_w.png'),
			FLAG_GERM: image.load('assets/Hud/Flags/e_germ_flag_w.png')}

	MISSION_BUILDING = 0
	MISSION_ICONS = {MISSION_BUILDING: image.load('assets/Hud/miss_enter_bldg.png'),
			}

	HEAD_ICONS = {BLUE: (image.load('assets/Hud/head_blu_hat.png'),
							image.load('assets/Hud/head_blu_nohat.png')),
					YELLOW: (image.load('assets/Hud/head_yel_hat.png'),
							image.load('assets/Hud/head_yel_nohat.png')),
					GREEN: (image.load('assets/Hud/head_gre_hat.png'),
							image.load('assets/Hud/head_gre_nohat.png')),
					}

	BODY_ICONS = {BLUE: image.load('assets/Hud/body_blu.png'),
					YELLOW: image.load('assets/Hud/body_yel.png'),
					GREEN: image.load('assets/Hud/body_gre.png'),
					}

	background = image.SolidColorImagePattern(color=(255, 255, 255, 255))\
			.create_image(256, 180)

	def __init__(self, id):
		self.id = id
		self.mission = None
		self.mission_target = None
		self.mission_cooldown = 5.0

		self.death_count = 0
		self.name = "fdsa"

		self._score = 0

		self.name_label = text.Label(text = self.name,\
				font_name="Courier New", font_size=20, bold=True,\
				color=(0,0,0,255), halign='center',\
				x = 3, y = self.get_offset_y() + 3, width = 140, height = 40)

		self.score_label = text.Label(\
				font_name="Arial Black", font_size=18,\
				color=(0,0,0,255), halign='center',\
				x = 150, y = self.get_offset_y() + 3, width = 103, height = 40)

		self.score = 0

	def getscore(self):
		return self._score

	def setscore(self, value):
		self._score = value
		self.score_label.text = "S: " + str(value)

	score = property(getscore, setscore)

	def update(self, time):
		self.mission_cooldown -= time
		if self.mission_cooldown < 0.0 and self.mission == None:
			# no mission and cooldown's up, get a new mission
			self.mission = self.MISSION_BUILDING
			self.mission_target = random.choice(range(16))
			print "Player ", self.id, " has received a mission to go to ", self.mission_target

	def get_dude(self):
		return World.get_world().dudes[self.id]

	def get_offset_y(self):
		return 768 - ((self.id + 1) * 180)

	def draw_hud(self):
		offset_y = self.get_offset_y()

		self.background.blit(0, offset_y)

		self.FLAG_ICONS[self.id].blit(3, offset_y + 180 - 3 - 4 - 52)

		if self.mission != None:
			self.MISSION_ICONS[self.mission].blit(94, offset_y + 180 - 63)
			target_building = World.get_world().buildings[self.mission_target]
			Building.BUILDING_TYPE[target_building.type][2].blit(94, offset_y + 180 -63 - 67)

		dude = self.get_dude()
		if (dude.outfit == HAT):
			head = 0
		else:
			head = 1

		self.HEAD_ICONS[dude.colour][head].blit(94 + 60 + 7, offset_y + 180 - 3 - 43)
		self.BODY_ICONS[dude.colour].blit(94 + 60 + 7, offset_y + 180 - 3 - 43 - 84)

		self.name_label.draw()
		self.score_label.draw()

# x = 94

	def complete_mission(self):
		print "Player ", self.id, " has completed a mission"
		self.score += 1
		self.mission = None
		self.mission_cooldown = 7.0

	def mission_target_bombed(self):
		self.mission = None
		self.mission_cooldown = 7.



class World:
	is_server = True
	batch = graphics.Batch()

	def __init__(self, state = None):
		self.buildings = []
		self.dudes = []
		self.background = image.load('assets/city_all.png')
		self.hud_mockup = image.load('assets/hud_mockup.png')
		self.doors = []

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
				self.add_door(building)

			for i in xrange(20):
				self.add_dude()

			World.my_player_id = self.allocate_new_playerid()
		else:
			# construct from given state
			(building_state, dude_state) = state

			for i in xrange(len(building_state)):
				building = Building(i, state=building_state[i])
				self.buildings.append(building)
				self.add_door(building)

			self.dudes = [Dude(state=s) for s in dude_state]

	__instance = None
	@classmethod
	def get_world(cls):
		return cls.__instance

	@classmethod
	def set_world(cls, world):
		cls.__instance = world

	def allocate_new_playerid(self, suppressUpdate=False):
		if not None in self.players:
			return None

		player_id = self.players.index(None)

		if player_id > len(self.dudes):
			print "No dudes to take control of!"
			return None

		self.players[player_id] = Player(player_id)
		self.dudes[player_id].take_control_by(player_id, suppressUpdate)

		return player_id


	def add_dude(self):
		d = Dude(id = len(self.dudes))
		d.randomise()
		self.dudes.append(d)

	def nearest_dude_to(self, dude):
		x1, y1 = dude.xy()
		mindist = None
		nearestDude = None
		for d in self.dudes:
			if d is dude: continue
			if not d.alive: continue
			x2, y2 = d.xy()
			dy = y2 - y1
			dx = x2 - x1
			dist = math.sqrt(dy*dy + dx*dx)
			if dist < 100 and (mindist is None or dist < mindist):
				mindist = dist
				nearestDude = d

		return nearestDude

	def add_door(self, building):
		# building ID determines location
		x = (28 + 202 * (building.id % 4))/768.
		y = (28 + 202 * (building.id / 4))/768.
		# door ID determines path and location float
		doorx, doory = building.BUILDING_TYPE[building.type][1]
		if doorx == 0:
			# left path
			path = (building.id % 4) * 2 + 8
			door_location = y + doory
#			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location
			self.doors.append((path, door_location))

		if doorx == 1:
			# right path
			path = (building.id % 4) * 2 + 9
			door_location = y + doory
#			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location
			self.doors.append((path, door_location))

		if doory == 0:
			# lower path
			path = (building.id / 4) * 2
			door_location = x + doorx
#			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location
			self.doors.append((path, door_location))

		if doory == 1:
			# upper path
			path = (building.id / 4) * 2 + 1
			door_location = x + doorx
#			print "Door from Building ", building.id, " is on path ", path, " location: ", door_location
			self.doors.append((path, door_location))
                
	def get_player(self, player_id):
		return self.dudes[player_id]

	def draw(self, window):
		# background
		self.background.blit(256,0)
#		self.hud_mockup.blit(0,0)

		self.draw_hud()

		for d in self.dudes:
			d.draw(window)

		for b in self.buildings:
			b.draw(window)

		player = self.get_player(World.my_player_id)
		nearest = self.nearest_dude_to(player)
		if nearest:
			xy = nearest.xy()
			self.crosshair.set_position(256 + 1 + xy[0], 1 + xy[1])
			self.crosshair.visible = True
		else:
			self.crosshair.visible = False

		World.batch.draw()

		# hud
		label = text.Label("FPS: %d" % clock.get_fps(), font_name="Georgia",
				font_size=24, x=0, y=7)
		label.draw()

	def draw_hud(self):
		for p in self.players:
			if p != None:
				p.draw_hud()

	def update(self, time):
		for b in self.buildings:
			b.update(time)

		for d in self.dudes:
			d.update(time)
			
		for p in self.players:
			if p != None:
				p.update(time)

	# For net sync
	def state(self):
		return ([b.state() for b in self.buildings], [d.state() for d in self.dudes])

	def update_dude(self, dude_state):
		self.dudes[dude_state[0]].update_local_state(dude_state)

	def remote_explode(self, state):
		terrorist_id, building_id = state

		self.buildings[building_id].explode()

class Building:
	TYPE_CLOTHES, TYPE_BOMB, TYPE_HOSPITAL, TYPE_MUSEUM,\
	TYPE_DISCO, TYPE_ARCADE, TYPE_CARPARK, TYPE_FACTORY,\
	TYPE_OFFICE, TYPE_PARK, TYPE_WAREHOUSE, TYPE_BANK,\
	TYPE_RESTAURANT, TYPE_TOWNHALL, TYPE_RADIO, TYPE_CHURCH = range(16)
	
	BOMB_SOUND = resource.media('assets/Bomb Detonation.wav', streaming=False)

	BUILDING_TYPE = {
			TYPE_CLOTHES: (image.load('assets/Building_assets/clothes_test.png'), (0.139, 0),
				image.load('assets/Building_Icons/clothes_icon.png')),
			TYPE_BOMB: (image.load('assets/Building_assets/bomb_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/bomb_icon.png')),
			TYPE_HOSPITAL: (image.load('assets/Building_assets/hospital_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/hospital_icon.png')),
			TYPE_MUSEUM: (image.load('assets/Building_assets/museum_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/museum_icon.png')),
			TYPE_DISCO: (anim.load_anim('Building_assets/Disco_Anim', fps=2), (1, 0.139),
				image.load('assets/Building_Icons/club_icon.png')),
			TYPE_ARCADE: (image.load('assets/Building_assets/arcade_test.png'), (0, 0.139),
				image.load('assets/Building_Icons/arcade_icon.png')),
			TYPE_CARPARK: (image.load('assets/Building_assets/carpark_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/parking_icon.png')),
			TYPE_FACTORY: (image.load('assets/Building_assets/factory_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/factory_icon.png')),
			TYPE_OFFICE: (image.load('assets/Building_assets/office_test.png'), (0.139, 1),
				None),
#				image.load('assets/Building_Icons/office_icon.png')),
			TYPE_PARK: (anim.load_anim('Building_assets/Park_Anim', fps=2), (0.139, 1),
				image.load('assets/Building_Icons/park_icon.png')),
			TYPE_WAREHOUSE: (image.load('assets/Building_assets/warehouse_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/warehouse_icon.png')),
			TYPE_BANK: (image.load('assets/Building_assets/bank_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/bank_icon.png')),
			TYPE_RESTAURANT: (image.load('assets/Building_assets/cafe_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/cafe_icon.png')),
			TYPE_TOWNHALL: (anim.load_anim('Building_assets/Hall_anim', fps=8), (0.139, 1),
				image.load('assets/Building_Icons/city_hall_icon.png')),
			TYPE_RADIO: (anim.load_anim('Building_assets/Radio_anim', fps=2), (0.139, 1),
				image.load('assets/Building_Icons/radio_icon.png')),
			TYPE_CHURCH: (image.load('assets/Building_assets/church_test.png'), (0.139, 1),
				image.load('assets/Building_Icons/church_icon.png')),
			}

	for k in BUILDING_TYPE:
		v = BUILDING_TYPE[k]
		if isinstance(v[0], image.AbstractImage):
			v[0].anchor_x = v[0].width // 2
			v[0].anchor_y = v[0].height // 2

	EXPLOSION = anim.load_anim('Explosion', loop=False)
	DOOR_LIGHT = image.load('assets/light_beam.png')

	def __init__(self, id, type=None, state=None):
		self.id = id
		self.type = type
		self.has_bomb = False
		self.blownup_cooldown = 0

		if state != None:
			(self.type, self.has_bomb, self.blownup_cooldown) = state

		self.sprite = sprite.Sprite(self.BUILDING_TYPE[self.type][0],
				group=anim.ROOF, batch=World.batch)
		self.sprite.x = 256 + 1 + 28 + 202 * (id % 4) + 104/2
		self.sprite.y = 1 + 28 + 202 * (id / 4) + 104/2

		self.light = sprite.Sprite(self.DOOR_LIGHT, group=anim.PATH,
				batch=World.batch)
		door_loc = self.BUILDING_TYPE[self.type][1]

		x = 256 + 1 + 28 + 202 * (id % 4)
		y = 1 + 28 + 202 * (id / 4)

		# this just sets left/right, top/bottom
		self.light.x = x + door_loc[0] * 104
		self.light.y = y + door_loc[1] * 104

		# now we set location on the side
		if door_loc[0] == 0: # left-hand side
			self.light.rotation = -90
			self.light.y = y + (door_loc[1] - 0.069/2) * 768 - self.light.image.width // 2 - 28
		elif door_loc[0] == 1: # right-hand side
			self.light.rotation = 90
			self.light.y = y + (door_loc[1] - 0.069/2) * 768 + self.light.image.width // 2 - 28
		elif door_loc[1] == 0: # bottom side
			self.light.rotation = 180
			self.light.x = x + (door_loc[0] - 0.069/2) * 768 + self.light.image.width // 2 - 28
		elif door_loc[1] == 1: # top side
			self.light.rotation = 0
			self.light.x = x + (door_loc[0] - 0.069/2) * 768 - self.light.image.width // 2 - 28

		self.explosion_sprite = None
		self.exploding = False
	
	def draw(self, window):
		#self.light.draw()
		#self.sprite.draw()
		#if self.explosion_sprite:
			#self.explosion_sprite.draw()
		pass

	def update(self, time):
		pass

	def explode(self):
		if self.exploding: return
		
		broadcast_building_explosion((World.my_player_id, self.id))
		self.BOMB_SOUND.play()
		self.exploding = True
		def explosion_animation(dt):
			self.explosion_sprite = sprite.Sprite(self.EXPLOSION, group=anim.SKY,
					batch=World.batch)
			self.explosion_sprite.x = 256 + 1 + 28 + 202 * (self.id % 4) + 104/2
			self.explosion_sprite.y = 1 + 28 + 202 * (self.id / 4) + 104/2

			@self.explosion_sprite.event
			def on_animation_end():
				del self.explosion_sprite
				self.explosion_sprite = None
				self.exploding = False

		clock.schedule_once(explosion_animation, 0.6)

	def state(self):
		return (self.type, self.has_bomb, self.blownup_cooldown)

from Dude import *
from net import broadcast_building_explosion
