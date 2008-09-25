#!/usr/bin/env python

from pyglet import *
from pyglet.gl import *
from mtpyglet import TouchWindow

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
		
		
		
		
class TouchAppWindow(TouchWindow):
	def __init__(self, widget, config=None):
		config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
		TouchWindow.__init__(self, config)
		self.root_widget = widget
		self.root_widget.window = self

	def on_draw(self):
		self.clear()
		self.root_widget.draw()
		
		
		
		
		
class Widget(object):
	def __init__(self, parent=None):
		self.parent = parent
		if self.parent:
			self.window = parent.window

	def draw(self):
		pass

	def show_in_window(self):
		config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
		self.window = TouchAppWindow(self, config=config)
		return self.window
		#runTouchApp()