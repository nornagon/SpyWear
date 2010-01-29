#!/usr/bin/python

from pyglet import *
from model import *

WIDTH = 1024
HEIGHT = 768

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
	world.draw(window)

d = Dude()

def update(dt):
	d.location += 0.001
	world.update(dt)

clock.schedule(update)

for i in xrange(16):
	world.buildings.append(Building(i))

world.dudes.append(d)

app.run()

