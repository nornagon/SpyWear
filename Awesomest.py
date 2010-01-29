#!/usr/bin/python

from pyglet import *
from model import *

WIDTH = 1024
HEIGHT = 768

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
	world.draw(window)

def update(dt):
	world.update(dt)

clock.schedule(update)

app.run()

