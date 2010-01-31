from pyglet import *
import os, glob

OVERLAY = graphics.OrderedGroup(15) # win,loss
SKY = graphics.OrderedGroup(10) # explosions, crosshair
ROOF = graphics.OrderedGroup(8) # building tops
GROUND = graphics.OrderedGroup(6) # on the footpath
MARKER = graphics.OrderedGroup(5) # dude's marker
PATH = graphics.OrderedGroup(4) # the footpath

def load_anim(path, fps=24, loop=True, anchor_center=True):
	jn = os.path.join
	files = glob.glob(jn('assets', path, '*.png'))
	files.sort()
	images = [image.load(f) for f in files]
	if anchor_center:
		for img in images:
			img.anchor_x = img.width // 2
			img.anchor_y = img.height // 2
	return image.Animation.from_image_sequence(images, 1.0/fps, loop)

def load_anim_bounce(path, fps, loop=True):
	jn = os.path.join
	files = glob.glob(jn('assets', path, '*.png'))
	files.sort()
	images = [image.load(f) for f in files]
	for img in images:
		img.anchor_x = img.width // 2
		img.anchor_y = img.height // 2

	images_backwards = images[:]
	images_backwards.reverse()
	images_backwards = images_backwards[:-1]
	images.extend(images_backwards)

	return image.Animation.from_image_sequence(images, 1.0/fps, loop)
