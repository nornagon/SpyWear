#!/usr/bin/python

import sys
from pyglet import *
import pygletreactor
pygletreactor.install()
from model import *
from net import *


from twisted.internet import reactor

WIDTH = 1024
HEIGHT = 768

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
	world.draw(window)

@window.event
def on_close():
	print "stopping"
	app.exit()
#	reactor.stop()
	return event.EVENT_HANDLED

def update(dt):
	world.update(dt)

clock.schedule(update)

if sys.argv[0] == '-h':
	print "server mode"

reactor.run(call_interval=1/60.)
#app.run()

