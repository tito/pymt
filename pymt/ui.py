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
		




class Widget(object):
	def __init__(self, parent=None):
		self.parent = parent
		
	def draw(self):
		pass


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
		self.position = pos
		self.size = size
		
	def draw(self):
		drawRectangle(self.position ,self.size)
		
	def collidePoint(self, x,y):
		if( x > self.position[0]  and x < self.position[0] + self.size[0] and
		    y > self.position[1]  and y < self.position[1] + self.size[1]  ):
			return True


		
class DragableObject(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)
		self.state = ('normal', None)
	
		
	def on_touch_down(self, touches, touchID, x, y):
		if self.collidePoint(x,y):
			self.state = ('dragging', touchID, x, y)
			return True
	def on_touch_move(self, touches, touchID, x, y):
		if self.state[0] == 'dragging' and self.state[1]==touchID:
			self.position = (self.position[0] + (x - self.state[2]) , self.position[1] + y - self.state[3])
			self.state = ('dragging', touchID, x, y)
                        return True
	def on_touch_up(self, touches, touchID, x, y):
		if self.state[1] == touchID:
			self.state = ('normal', None)
                        return True
		


class Button(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent)
		self.position = pos
		self.size = size
		self.state = ('normal', 0)
		self.clickActions = []

		
	def draw(self):
		if self.state[0] == 'down':
			drawRectangle(self.position ,self.size, color=(0.5,0.5,0.5))
		else:
			drawRectangle(self.position ,self.size)

		
	def on_touch_down(self, touches, touchID, x, y):
		if self.collidePoint(x,y):
			self.state = ('down', touchID)
			return True
	def on_touch_move(self, touches, touchID, x, y):
		if self.state[1] == touchID and not self.collidePoint(x,y):
			self.state = ('normal', 0)
                        return True
	def on_touch_up(self, touches, touchID, x, y):
		if self.state[1] == touchID and self.collidePoint(x,y):
			self.state = ('normal', 0)
			for callback in self.clickActions:
				callback()
			return True
                        
                        
class ImageButton(Button):
    def __init__(self, image_file, parent=None, pos=(0,0), size=(100,100)):
        Button.__init__(self,parent,pos,size)
        
        img = pyglet.image.load(image_file)
        img.anchor_x = img.width/2
        img.anchor_y = img.height/2
        
        self.original_pos = pos
        self.interpolator = 0.0
        
        self.image = pyglet.sprite.Sprite(img)
        self.image.x, self.image.y = self.position
        self.image.scale = 0.2
        
        self.target_scale = self.image.scale
        self.target_position = self.position
        self.size = (self.image.width, self.image.height)
        
    def draw(self):
        self.image.x, self.image.y = self.position
        self.update()
        self.update()
        self.image.draw()
        
    def setBig(self):
        self.interpolator = 0.0
        self.target_scale = 1.0
        self.target_position = (900,600)
        
    def setSmall(self):
        self.interpolator = 0.0
        self.target_scale = 0.2
        self.target_position = self.original_pos
    
    def collidePoint(self, x,y):
            if( x > self.position[0]- self.size[0]/2  and x < self.position[0] + self.size[0]/2 and
                y > self.position[1]- self.size[0]/2  and y < self.position[1] + self.size[1]/2  ):
                    return True
        
    def update(self):
        if self.target_scale > self.image.scale:
            self.image.scale +=0.02
        if self.target_scale < self.image.scale:
            self.image.scale -=0.02
           
        self.interpolator = min(self.interpolator + 0.02, 1.0)
        self.position = (self.target_position[0]*self.interpolator + self.position[0] * (1-self.interpolator),
                         self.target_position[1]*self.interpolator + self.position[1] * (1-self.interpolator) )
        
        self.size = (self.image.width, self.image.height)

