#!/usr/bin/python

import sys
from pyglet import *
from pyglet.window import key
from model import *
from net import *
import random

from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall

WIDTH = 1024
HEIGHT = 768

World.my_player_id = 0

random.seed()

window = window.Window(width=1024, height=768)
window.clear()

@window.event
def on_draw():
	window.clear()
	world.draw(window)

@window.event
def on_close():
	window.close()
	reactor.stop()
	return True

keybindings = {key.W : UP, key.UP : UP, key.A : LEFT, key.LEFT : LEFT,
	       key.S : DOWN, key.DOWN : DOWN, key.D : RIGHT, key.RIGHT : RIGHT}

@window.event
def on_key_press(symbol, modifiers):
	dude = world.get_player(World.my_player_id)

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

def update(dt):
	world.update(dt)

clock.schedule(update)

if len(sys.argv) >= 2 and sys.argv[1] == '-h':
	world_deferred = defer.maybeDeferred(server_world)
elif len(sys.argv) >= 2:
	world_deferred = defer.maybeDeferred(client_world, sys.argv[1])
else:
	def local_world(): return (0, World())
	world_deferred = defer.maybeDeferred(local_world)

def pygletPump():
	clock.tick(poll=True)

	for window in app.windows:
		window.switch_to()
		window.dispatch_events()
		window.dispatch_event('on_draw')
		window.flip()

def run((playerId, _world)):
	World.my_player_id = playerId
	World.set_world(_world)
	global world
	world = _world
	LoopingCall(pygletPump).start(1/60.0)

world_deferred.addCallback(run)
reactor.run()
