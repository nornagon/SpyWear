#!/usr/bin/python

import sys
from pyglet import *
from pyglet.window import key
from model import *
from net import *
import random

from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall

class StateController:
	def __init__(self, dispatcher):
		self.dispatcher = dispatcher
		self.state = None

	def switch(self, new_state):
		if self.state:
			self.state.deactivate(self.dispatcher)
		self.state = new_state
		self.state.activate(self.dispatcher)

class GameState:
	def __init__(self):
		pass

	def activate(self, dispatcher):
		handlers = filter(lambda x: x[:3] == 'on_', dir(self))
		handler_dict = {}
		for h in handlers:
			handler_dict[h] = getattr(self, h)

		dispatcher.push_handlers(**handler_dict)
		self.scheduled = lambda dt: self.update(dt)
		clock.schedule(self.scheduled)

	def deactivate(self, dispatcher):
		dispatcher.pop_handlers()
		clock.unschedule(self.scheduled)

	def update(self, dt):
		pass

WIDTH = 1024
HEIGHT = 768

AMBIENT_AUDIO = resource.media('assets/Ambient City.mp3', streaming=True)
AMBIENT_MUSIC = resource.media('assets/Theme.mp3', streaming=True)

World.my_player_id = 0

random.seed()

window = window.Window(width=1024, height=768)
window.clear()

@window.event
def on_close():
	window.close()
	reactor.stop()
	return True

keybindings = {key.W : UP, key.UP : UP, key.A : LEFT, key.LEFT : LEFT,
	       key.S : DOWN, key.DOWN : DOWN, key.D : RIGHT, key.RIGHT : RIGHT}

class MainState(GameState):
	def __init__(self, world):
		self.world = world

	def on_draw(self):
		window.clear()
		self.world.draw(window)

	def on_key_press(self, symbol, modifiers):
		dude = self.world.get_player_dude(World.my_player_id)

		if symbol in keybindings.keys():
			dude.turn(keybindings[symbol])
		elif symbol == key.SPACE:
			dude.stopstart()
		elif symbol == key.ENTER:
			dude.enter()
		elif symbol == key.B:
			dude.bomb()
		elif symbol == key.V:
			dude.shoot()

		dude.reset_idle_timer()

	def update(self, dt):
		self.world.update(dt)

class MenuState(GameState):
	def __init__(self):
		self.connecting = False
		self.host_batch = graphics.Batch()
		self.title = text.Label('SpyWear', font_name='Courier New', font_size=48,
				bold=True, anchor_x='center', x=WIDTH//2, y=700)

		self.host_label = text.Label('Connect:', font_name='Courier New',
				font_size=36, x=50, y=300, batch=self.host_batch)

		self.host_entry = text.document.UnformattedDocument()
		self.host_entry.set_style(0, len(self.host_entry.text), {'bold':True,
			'font_name':'Courier New', 'font_size':36, 'color':(255,255,255,255)})

		self.host_entry_layout = text.layout.IncrementalTextLayout(self.host_entry,
				400, 60, batch=self.host_batch)
		self.host_entry_layout.x = 350
		self.host_entry_layout.y = 300
		self.host_entry_layout.anchor_y = self.host_label.anchor_y

		self.caret = text.caret.Caret(self.host_entry_layout, color=(255,255,255))
		self.caret.on_layout_update()

		self.underline = self.host_batch.add(2, pyglet.gl.GL_LINES, None,
				('v2i', [350,295, 750,295]),
				('c4B', [255,255,255,255] * 2)
			)

		self.instruction_batch = graphics.Batch()
		self.instructions_document = text.decode_attributed(u"""

{font_name "Courier New"}{font_size 36}{color (255,255,255,255)}{.align 'center'}Welcome to SpyWear!

{.align 'center'}Press {bold True}C{bold False} to connect to a server{}
Press {bold True}H{bold False} to host a game
""")
		self.instructions_layout = \
				text.layout.TextLayout(self.instructions_document,
					batch=self.instruction_batch, multiline=True, width=1024)
		self.instructions_layout.y = 200

		import socket
		ip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][0]
		self.ip_label = text.Label("Your IP is: " + ip,
				batch=self.instruction_batch, anchor_x='center', x=WIDTH//2, y=100,
				font_name='Courier New', font_size=24)

	def on_draw(self):
		window.clear()
		self.title.draw()

		if self.connecting is None:
			self.connecting = True
		if self.connecting:
			self.host_batch.draw()
		else:
			self.instruction_batch.draw()

	def on_key_press(self, symbol, modifiers):
		if self.connecting:
			if symbol == key.ESCAPE:
				self.connecting = False
				return True
			elif symbol == key.ENTER:
				self.connect(self.host_entry.text.strip())
		else:
			if symbol == key.H:
				self.host()
			elif symbol == key.C:
				self.connecting = None

	def on_text(self, text):
		if text == u'\r': return
		if self.connecting:
			self.caret.on_text(text)
	def on_text_motion(self, motion):
		if self.connecting:
			self.caret.on_text_motion(motion)
	def on_text_motion_select(self, motion):
		if self.connecting:
			self.caret.on_text_motion_select(motion)

	def host(self):
		world_deferred = defer.maybeDeferred(server_world)
		world_deferred.addCallback(run)

	def connect(self, host):
		world_deferred = defer.maybeDeferred(client_world, host)
		world_deferred.addCallback(run)

def run((playerId, _world)):
	World.my_player_id = playerId
	World.set_world(_world)

	state_controller.switch(MainState(_world))

	player = media.Player()
	player.eos_action = 'loop'
	player.queue(AMBIENT_AUDIO)
	player.play()
	player2 = media.Player()
	player2.eos_action = 'loop'
	player2.queue(AMBIENT_MUSIC)
	player2.play()


def pygletPump():
	clock.tick(poll=True)

	for window in app.windows:
		window.switch_to()
		window.dispatch_events()
		window.dispatch_event('on_draw')
		window.flip()

state_controller = StateController(window)
state_controller.switch(MenuState())

LoopingCall(pygletPump).start(1/60.0)

reactor.run()
