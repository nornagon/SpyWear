#!/usr/bin/python

import sys
from pyglet import *
from model import *
from net import *
import random

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

WIDTH = 1024
HEIGHT = 768

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
