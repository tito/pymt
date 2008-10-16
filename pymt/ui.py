#!/usr/bin/env python

from pyglet import *
from pyglet.gl import *
from mtpyglet import TouchWindow
from graphx import *

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
		
		
		
		
class MTContext(object):
	pass



class UIWindow(TouchWindow):
	def __init__(self, view):
		config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
		TouchWindow.__init__(self, config)
		#self.set_fullscreen()
		self.active_view = view
		self.active_view.parent = self
	
	def on_draw(self):
		self.clear()
		self.active_view.draw()

	def on_touch_down(self, touches, touchID, x, y):
		#print "test", self.active_view
		self.active_view.on_touch_down(touches, touchID, x, y)
	
	def on_touch_move(self, touches, touchID, x, y):
		self.active_view.on_touch_move(touches, touchID, x, y)

	def on_touch_up(self, touches, touchID, x, y):
		self.active_view.on_touch_up(touches, touchID, x, y)
		

class Animation(object):
	def __init__(self, widget, label, prop, to, timestep, length):
		self.widget = widget
		self.frame = 0.0
		self.prop = prop
		self.to = to
                self.fro = self.widget.__dict__[self.prop]
		self.timestep = timestep
		self.length = length
		self.label = label
		
	def get_current_value(self):
		return  (1.0-self.frame/self.length) * self.fro  +  self.frame/self.length * self.to 
		
	def start(self):
		#print 'calling'
		self.reset()
		pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
		
	def reset(self):
                self.fro = self.widget.__dict__[self.prop]
		self.frame = 0.0
		
	def advance_frame(self, dt):
		self.frame += self.timestep
		self.widget.__dict__[self.prop] = self.get_current_value()
		if self.frame < self.length:
			pyglet.clock.schedule_once(self.advance_frame, 1/60.0)

		


class Widget(object):
	def __init__(self, parent=None):
		self.parent = parent
		self.animations = []
		
	def draw(self):
		pass
		
	def add_animation(self, label, prop, to , timestep, length):
		anim = Animation(self, label, prop, to, timestep, length)
		self.animations.append(anim)
		return anim
		
	def start_animations(self, label='all'):
		for anim in self.animations:
			if anim.label == label or label == 'all':
				anim.reset()
				anim.start()
		


class MTWidget(Widget):
	def __init__(self, parent=None):
		Widget.__init__(self, parent)
	
	def on_touch_down(self, touches, touchID, x, y):
		#print "touchdown"
		pass
		
	def on_touch_move(self, touches, touchID, x, y):
		pass

	def on_touch_up(self, touches, touchID, x, y):
		pass
		



class Container(object):
	def __init__(self, parent=None):
		self.parent = parent
		self.widgets = []
	
	def add_widget(self,w):
		self.widgets.append(w)
		
	def draw(self):
		for w in self.widgets:
			w.draw()

	def on_touch_down(self, touches, touchID, x, y):
		for w in reversed(self.widgets):
		    if w.on_touch_down(touches, touchID, x, y):
		        break
		
	def on_touch_move(self, touches, touchID, x, y):
		for w in reversed(self.widgets):
		    if w.on_touch_move(touches, touchID, x, y):
		        break

	def on_touch_up(self, touches, touchID, x, y):
		for w in reversed(self.widgets):
		    if w.on_touch_up(touches, touchID, x, y):
		        break


class RectangularWidget(MTWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		MTWidget.__init__(self,parent)
		self.x, self.y = pos
		self.width, self.height = size
		
	def draw(self):
		drawRectangle((self.x, self.y) ,(self.width, self.height))
                
        
		
	def collidePoint(self, x,y):
		if( x > self.x  and x < self.x + self.width and
		    y > self.y and y < self.y + self.height  ):
			return True


		
class DragableWidget(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)
		self.state = ('normal', None)
	
		
	def on_touch_down(self, touches, touchID, x, y):
		if self.collidePoint(x,y):
			self.state = ('dragging', touchID, x, y)
			return True
	def on_touch_move(self, touches, touchID, x, y):
		if self.state[0] == 'dragging' and self.state[1]==touchID:
			self.x, self.y = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
			self.state = ('dragging', touchID, x, y)
                        return True
	def on_touch_up(self, touches, touchID, x, y):
		if self.state[1] == touchID:
			self.state = ('normal', None)
                        return True
		


class Button(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)

		self.state = ('normal', 0)
		self.clickActions = []

		
	def draw(self):
		if self.state[0] == 'down':
			drawRectangle((self.x,self.y) , (self.width, self.height), color=(0.5,0.5,0.5))
		else:
			drawRectangle((self.x,self.y) , (self.width, self.height))

		
	def on_touch_down(self, touches, touchID, x, y):
		if self.collidePoint(x,y):
			self.state = ('down', touchID)
			return True
	def on_touch_move(self, touches, touchID, x, y):
		if self.state[1] == touchID and not self.collidePoint(x,y):
			self.state = ('normal', 0)
                        return True
	def on_touch_up(self, touches, touchID, x, y):
		#print x,y , self.collidePoint(x,y)
		if self.state[1] == touchID and self.collidePoint(x,y):
			self.state = ('normal', 0)
			for callback in self.clickActions:
				callback()
			return True
                

class TestImageButton(Button):
    def __init__(self, image_file, parent=None, pos=(0,0), size=(1,1), scale = 0.16):
        Button.__init__(self,parent,pos,size)
        img = pyglet.image.load(image_file)

        self.image = pyglet.sprite.Sprite(img)
        self.image.x, self.image.y = self.x, self.y
        self.scale =  scale
        self.image.scale = self.scale
        self.width, self.height = (self.image.width, self.image.height)
                       
    def draw(self):
        self.image.x, self.image.y = (self.x, self.y)
        self.image.scale = self.scale
        self.width, self.height = (self.image.width, self.image.height)
        self.image.draw()
       