import math

class Node:
	def __init__(self, x, y, edges=None):
		self.x = x
		self.y = y
		if edges is None:
			self.edges = {}
		else:
			self.edges = edges
		self.id = None

	def distanceTo(self, dir):
		dx = self.edges[dir].x - self.x
		dy = self.edges[dir].y - self.y
		return math.sqrt(dx*dx+dy*dy)

	def pointAt(self, dir, pixels):
		dx = self.edges[dir].x - self.x
		dy = self.edges[dir].y - self.y
		d = math.sqrt(dx*dx+dy*dy)
		dx /= d
		dy /= d
		return (self.x + dx * pixels, self.y + dy * pixels)

class Map:
	def __init__(self):
		self.nodes = []

	def add_node(self, node):
		node.id = len(self.nodes)
		self.nodes.append(node)
