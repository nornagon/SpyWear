#!/usr/bin/python

from pyglet import *

WIDTH = 1024
HEIGHT = 768

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
	window.clear()

app.run()

