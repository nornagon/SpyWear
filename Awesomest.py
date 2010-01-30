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
myplayerID = 0

random.seed()

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
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
	if symbol in keybindings.keys():
	       world.get_player(myplayerID).turn(keybindings[symbol])
	if symbol == key.SPACE:
		world.get_player(myplayerID).stopstart()
	if symbol == key.ENTER:
		world.get_player(myplayerID).enter()
	if symbol == key.B:
		world.get_player(myplayerID).bomb()

def update(dt):
	world.update(dt)

clock.schedule(update)

if len(sys.argv) >= 2 and sys.argv[1] == '-h':
	world_deferred = defer.maybeDeferred(server_world)
elif len(sys.argv) >= 2:
	world_deferred = defer.maybeDeferred(client_world, sys.argv[1])
else:
	world_deferred = defer.maybeDeferred(local_world)

def pygletPump():
	clock.tick(poll=True)

	for window in app.windows:
		window.switch_to()
		window.dispatch_events()
		window.dispatch_event('on_draw')
		window.flip()

world = None
def run(_world):
	global world
	world = _world
	LoopingCall(pygletPump).start(1/60.0)

world_deferred.addCallback(run)
reactor.run()
