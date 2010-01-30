from pyglet import *
import os, glob

SKY = graphics.OrderedGroup(10)
ROOF = graphics.OrderedGroup(8)
PATH = graphics.OrderedGroup(6)
GROUND = graphics.OrderedGroup(4)

def load_anim(path, fps=24, loop=True):
	jn = os.path.join
	files = glob.glob(jn('assets', path, '*.png'))
	files.sort()
	images = [image.load(f) for f in files]
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
