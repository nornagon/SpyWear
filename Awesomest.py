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

@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.UP:
		world.get_player(myplayerID).turn(UP)
		print "turning UP"
	if symbol == key.DOWN:
		world.get_player(myplayerID).turn(DOWN)
		print "turning DOWN"
	if symbol == key.LEFT:
		world.get_player(myplayerID).turn(LEFT)
		print "turning LEFT"
	if symbol == key.RIGHT:
		world.get_player(myplayerID).turn(RIGHT)
		print "turning RIGHT"

def update(dt):
	world.update(dt)

clock.schedule(update)

if len(sys.argv) >= 2 and sys.argv[1] == '-h':
	print "server mode"
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
