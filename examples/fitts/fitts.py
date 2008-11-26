from pymt import *
from pyglet.gl import *
import time
from random import randint
from math import sqrt
import math
import pickle

#new experiment
#        2d fitts law study:  distances/position, sizes
#        log: position, size, time taken, errors=[time_into_trial, pos]
                
                
#from numpy import *
import ctypes
from random import randint
class Target(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
                s = randint(100,300)
                pos = (randint(100,900),randint(100,900))
                self.zoom =randint(1,3)
		RectangularWidget.__init__(self,parent, pos, (100.0,100.0))
                self.rotation = self._rotation = 60.0
                self.translation = Vector(self.x,self.y)
                self.label = label = pyglet.text.Label(str(self.zoom),
                font_name='Times New Roman',
                font_size=24,
                x=0, y=0,
                anchor_x='center', anchor_y='center')


        def draw(self):
                glPushMatrix()
                glTranslatef(self.translation[0], self.translation[1], 0)
                glRotatef(self.rotation , 0, 0, 1)
                glScalef(self.width*self.zoom, self.height*self.zoom, 1)
		glColor4f(0.3,0.3,0.3, 1.0)
                drawRectangle((-0.5, -0.5) ,(1, 1))
		glColor4f(0.5,0.3,0.3,1.0)
                drawTriangle(pos=(0.0,-0.25), w=0.6, h=0.6)
                
                self.label.text = str(self.zoom)
                glPushMatrix()
                glScalef(0.01,0.01,1.0)
                #self.label.draw()
                glPopMatrix()
                
                glPopMatrix()


class SourceWidget(ZoomableWidget):
        def __init__(self, target,parent=None, pos=(0,0), size=(100,100)):
                ZoomableWidget.__init__(self, parent=None, pos=pos, size=(100,100))
                self.color = (1.0, 1.0, 1.0, 0.5)
                self.target = target
                self.done = False
                
                self.log_buffer = []
                self.errors = []
                self.start_time = time.clock()
                
        def draw_widget(self):
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glColor4f(*self.color)
                drawRectangle((-0.5, -0.5) ,(1, 1))
		glColor4f(0.7,0.5,0.5,0.5)
                drawTriangle(pos=(0.0,-0.25), w=0.6, h=0.6)
                glDisable(GL_BLEND)
                
                #self.label.text = str(self.zoom)[:5]
                glPushMatrix()
                glScalef(0.01,0.01,1.0)
                #self.label.draw()
                glPopMatrix()
                
        def testStart(self,dt):
                self.color = (1.0, 1.0, 1.0, 0.5)
                x,y = randint(100,900), randint(100,900)
                self.translation = Vector(x,y)
                self._translation = Vector(x,y)
                self.done = False
                #self.rotation = randint(1,359)
                #self.zoom = 1.0
                
                self.target.translation = Vector(randint(100,900), randint(100,900))
                self.target.rotation = randint(1,359)
                self.target.zoom = randint(1,3)

        def on_touch_move(self, touches, touchID, x, y):
                ZoomableWidget.on_touch_move(self, touches, touchID, x, y)
                dist = Length(self.translation - self.target.translation)
                if dist < 20 and not self.done \
                and abs(self.zoom - t.zoom) < 0.2 \
                and abs(self.rotation - self.target.rotation) < 10:
                        self.color = (0,1,0,0.3)
                        self.done = True
                        pyglet.clock.schedule_once(curry(SourceWidget.testStart, self), 1)


	       
c = Container()
t = Target()
c.add_widget( t)
c.add_widget( SourceWidget(t,pos=(300,300))  )
c.add_widget( TouchDisplay(c) )

#t.start_trials(10)
#win.set_fullscreen()

win = UIWindow()
win.set_fullscreen()
win.add_widget(c)
runTouchApp()
