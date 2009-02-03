from pymt import *
from pyglet.gl import *
import time
from random import randint
from math import sqrt
import math
import pickle

# new experiment
#  - 2d fitts law study:  distances/position, sizes
#  - log: position, size, time taken, errors=[time_into_trial, pos]

# from numpy import *
import ctypes
from random import randint
class Target(MTWidget):
		def __init__(self, **kwargs):
			kwargs.setdefault('pos', (randint(100,900),randint(100,900)))
			kwargs.setdefault('size', (100,100))
			s = randint(100,300)
			self.zoom = randint(1,3)
			super(Target, self).__init__(**kwargs)
			self.rotation = self._rotation = 60.0
			self.translation = Vector(*self.center)
			self.label = label = pyglet.text.Label(str(self.zoom),
				font_name='Times New Roman',
				font_size=24,
				x=0, y=0,
				anchor_x='center', anchor_y='center')
                
		def draw(self):
				glPushMatrix()
				glTranslatef(self.translation.x, self.translation.y, 0)
				glRotatef(self.rotation , 0, 0, 1)
				glScalef(self.width*self.zoom, self.height*self.zoom, 1)
				glColor4f(0.5,0.3,0.3, 1.0)
				drawRectangle((-0.5, -0.5) ,(1, 1))
				glColor4f(0.8,0.3,0.3,1.0)
				drawTriangle(pos=(0.0,-0.25), w=0.6, h=0.6)
				glPopMatrix()

class MTSourceWidget(MTScatterWidget):
		def __init__(self, **kwargs):
			kwargs.setdefault('pos', (0,0))
			kwargs.setdefault('size', (100,100))
			kwargs.setdefault('target', None)
			super(MTSourceWidget, self).__init__(**kwargs)
			self.color = (1.0, 1.0, 1.0, 0.5)
			self.target = kwargs.get('target')
			self.done = False
			self.translation = Vector(*self.center)
			self.log_buffer = []
			self.errors = []
			self.start_time = time.clock()
		
		def draw(self):
				glPushMatrix()
				enable_blending()
				glColor4f(*self.color)
				drawRectangle((0,0) ,(self.width, self.height))
				glColor4f(0.3,0.8,0.3,0.5)
				drawTriangle(pos=(self.width*0.5,self.height*0.2), w=self.width*0.6, h=self.height*0.6)
				glPopMatrix()		
		
		def testStart(self,dt):
			self.color = (1.0, 1.0, 1.0, 0.5)
			self.x,self.y = randint(100,900), randint(100,900)
			self.translation = Vector(*self.center)
			self.done = False
			#self.rotation = randint(1,359)
			#self.zoom = 1.0
		
			self.target.x, self.target.y = (randint(100,900), randint(100,900))
			self.target.rotation = randint(1,359)
			self.target.zoom = randint(1,3)
		
		def on_touch_move(self, touches, touchID, x, y):
			MTScatterWidget.on_touch_move(self, touches, touchID, x, y)
			self.translation =Vector(*self.center)
			dist = Vector.length(self.translation - self.target.translation)
			if  dist < 10 and not self.done \
		    and abs(self.zoom - t.zoom) < 0.2 \
			and abs(self.rotation - self.target.rotation) < 5:
					self.color = (0,1,0,0.3)
					self.done = True
					pyglet.clock.schedule_once(self.testStart, 1)



c = MTWidget()
t = Target()
c.add_widget( t)
c.add_widget( MTSourceWidget(target=t,pos=(300,300))  )
#c.add_widget( MTDisplay(c) )

win = MTWindow(fullscreen=True)
win.add_widget(c)
runTouchApp()
