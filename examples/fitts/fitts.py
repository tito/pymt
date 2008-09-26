from pymt import *
import pyglet

image_file = pyglet.image.load('fitts.png')
image_sprite = pyglet.sprite.Sprite(image_file, x=50, y=50)
image_sprite.scale=0.1

image_file = pyglet.image.load('fitts_target.png')
image_target = pyglet.sprite.Sprite(image_file, x=200, y=400)
image_target.scale=0.1


class MTContext(object):
	pass


class Widget(object):
	def __init__(self, parent=None):
		self.parent = parent
		
	def draw(self):
		pass


class MTWidget(Widget):
	def __init__(self, parent=None):
		Widget.__init__(self, parent)
#		if isinstance(parent, pyglet.event.EventDispatcher):
#			parent.push_handlers([self.on_touch_down, self.on_touch_move,self.on_touch_up])
	
	def on_touch_down(self, touches, touchID, x, y):
		print "touchdown"
		
	def on_touch_move(self, touches, touchID, x, y):
		pass

	def on_touch_up(self, touches, touchID, x, y):
		pass
		



class Container(object):
	def __init__(self, parent=None):
		self.parent = parent
		self.widgets = []
	
	def addWidget(self,w):
		self.widgets.append(w)
		
	def draw(self):
		for w in self.widgets:
			w.draw()





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
		print "test", self.active_view
		self.active_view.on_touch_down(touches, touchID, x, y)
	
	def on_touch_move(self, touches, touchID, x, y):
		self.active_view.on_touch_move(touches, touchID, x, y)

	def on_touch_up(self, touches, touchID, x, y):
		self.active_view.on_touch_up(touches, touchID, x, y)
		
		
		
class DragableObject(MTWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		MTWidget.__init__(self,parent)
		self.position = pos
		self.size = size
		self.state = ('normal', None)
		
	def draw(self):
		drawRectangle(self.position ,self.size)
		
	def on_touch_down(self, touches, touchID, x, y):
		#print x,y, self.position, self.size
		if( x > self.position[0]  and x < self.position[0] + self.size[0] and
		    y > self.position[1]  and y < self.position[1] + self.size[1]  ):
			print "yeah"
			self.state = ('dragging', touchID)
			
	def on_touch_move(self, touches, touchID, x, y):
		print self.state ,self.position
		if self.state[0] == 'dragging' and self.state[1]==touchID:
			self.position = (x - self.size[0]/2,y - self.size[1]/2)
		
	def on_touch_up(self, touches, touchID, x, y):
		if self.state[1] == touchID:
			self.state = ('normal', None)
		
		
		




class FittsApp(MTWidget):
	def __init__(self, parent=None):
		MTWidget.__init__(self,parent)
		self.mode = 'selecting'
		

		
	def draw(self):
		image_target.draw()
		image_sprite.draw()


	def on_touch_down(self, touches, touchID, x, y):
		if self.mode == 'selecting':
			print x,y, image_sprite.x, image_sprite.y, image_sprite.x + image_sprite.width
			if  ( x > image_sprite.x  and x < image_sprite.x + image_sprite.width
			  and y > image_sprite.y  and y < image_sprite.y + image_sprite.height ):
				self.mode = 'dragging'

	
		
	def on_touch_move(self, touches, touchID, x, y):
		if self.mode == 'dragging':
			image_sprite.x = x - image_sprite.width/2
			image_sprite.y = y - image_sprite.height/2
			if  ( x > image_target.x  and x < image_target.x + image_target.width
			  and y > image_target.y  and y < image_target.y + image_target.height ):
				self.mode = 'finish'


	def on_touch_up(self, touches, touchID, x, y):
		if self.mode == 'selecting':
			pass #record selection error
		if self.mode == 'dragging':
			self.mode = 'selecting'
			pass #record drag error
		pass
		

	
	
w = UIWindow(DragableObject())
w.set_fullscreen()
runTouchApp()
