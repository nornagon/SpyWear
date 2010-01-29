#!/usr/bin/python

import sys
from pyglet import *
from pyglet.window import key
from model import *
from net import *
import random

from twisted.internet import reactor
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
        if symbol == key.DOWN:
                world.get_player(myplayerID).turn(DOWN)
        if symbol == key.LEFT:
                world.get_player(myplayerID).turn(LEFT)
        if symbol == key.RIGHT:
                world.get_player(myplayerID).turn(RIGHT)

def update(dt):
	world.update(dt)

clock.schedule(update)

if len(sys.argv) >= 2 and sys.argv[1] == '-h':
	print "server mode"
	world = server_world()
elif len(sys.argv) >= 2:
	world = client_world(sys.argv[1])
else:
	world = local_world()

def pygletPump():
	clock.tick(poll=True)

	for window in app.windows:
		window.switch_to()
		window.dispatch_events()
		window.dispatch_event('on_draw')
		window.flip()

LoopingCall(pygletPump).start(1/60.0)
reactor.run()
