#!/usr/bin/env python

from pyglet import *
from pyglet.gl import *

class ColorPicker:
	def __init__(self, width=200, height = 400):
		self.width, self.height = width, height
		#draw a rectangle on the left hand side
		self.vertex_list = graphics.vertex_list(4,
                                          ('v2f', (40.0, 100.0,  float(width),100.0 ,  float(width),float(height)-50 ,  40.0, float(height)-50)) ,
                                          ('c4B', (0,0,0,255, 255,0,0,255, 255,255,0,255, 0,255,0,255) ) )
	def getColorForPoint(self,x,y):
		if x < self.width and y < self.height:
			return [float(x)/self.width, float(y)/self.height, 0.0]
		else: return None

	def draw(self):
		self.vertex_list.draw(GL_QUADS)