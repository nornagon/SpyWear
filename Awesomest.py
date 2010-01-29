#!/usr/bin/python

import sys
from pyglet import *
from model import *
from net import *

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

WIDTH = 1024
HEIGHT = 768

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
	world.draw(window)

@window.event
def on_close():
	print "stopping"
	reactor.stop()
	return True

def update(dt):
	d.location += 0.001
	world.update(dt)

clock.schedule(update)


d = Dude()

for i in xrange(16):
	world.buildings.append(Building(i))

world.dudes.append(d)

if sys.argv[1] == '-h':
	print "server mode"
	start_server()


if sys.argv[0] == '-h':
	print "server mode"
	start_server()


def pygletPump():
	clock.tick(poll=True)

	for window in app.windows:
		window.switch_to()
		window.dispatch_events()
		window.dispatch_event('on_draw')
		window.flip()

LoopingCall(pygletPump).start(1/60.0)
reactor.run()
