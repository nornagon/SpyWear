#!/usr/bin/python

from pyglet import *

window = window.Window(width=1024, height=768)

@window.event
def on_draw():
	window.clear()

app.run()

