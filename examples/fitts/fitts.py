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



        
class SelectionTask(Button):
        def __init__(self):
                Button.__init__(self)
                self.log_buffer = []
                self.errors = []
                self.start_time = time.clock()
                self.clickActions.append(self.finish_trial) 
                
        def start_trials(self, count):
                errors = []
                self.trial_counter = count
                size = randint(30, 150)
                self.width, self.height = size, size
                
                newx, newy = randint(0, self.parent.width), randint(0, self.parent.height)
                dx, dy = abs(self.x - newx), abs(self.y - newy)
                self.distance_to_last_point = sqrt(  dx*dx + dy*dy)
                self.x, self.y = newx, newy
                
        def finish_trial(self):
                self.log_buffer.append( [self.current_duration(), self.x, self.y, self.width, self.distance_to_last_point, self.errors] )
                if self.trial_counter > 0:
                        self.start_trials(self.trial_counter - 1)
                else:
                        self.finish_trials()
                        
        def finish_trials(self):
                output = open('data1.pkl', 'wb')
                pickle.dump(self.log_buffer, output)
                output.close()
                pyglet.app.exit()
                
        def current_duration(self):
                return time.clock() - self.start_time
        
	def on_touch_down(self, touches, touchID, x, y):
                if not Button.on_touch_down(self, touches, touchID, x, y):
                        #print "error"
                        self.errors.append([self.current_duration(), 'touch_down',x, y])
                        
	def on_touch_move(self, touches, touchID, x, y):
		if not Button.on_touch_move(self, touches, touchID, x, y):
                        self.errors.append([self.current_duration(), 'touch_move',x, y])
                
	def on_touch_up(self, touches, touchID, x, y):
		if not Button.on_touch_up(self, touches, touchID, x, y):
                        self.errors.append([self.current_duration(), 'touch_up',x, y])
                
                
                
#from numpy import *
import ctypes

class Target(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)
                self.rotation = self._rotation = 60.0


        def draw(self):
                glPushMatrix()
                glTranslatef(self.x, self.y, 0)
                glRotatef(-1.0*self.rotation , 0, 0, 1)
                glScalef(self.width, self.height, 1)
                drawRectangle((-0.5, -0.5) ,(1, 1),color=(0.7,0.8,0.8))
                drawTriangle(pos=(100,100), w=100, h=200)
                glPopMatrix()


                
                
c = Container()
c.add_widget( ZoomableWidget(pos=(300,300))  )
c.add_widget( Target(pos=(700,500)) )
c.add_widget( TouchDisplay(c) )
win = UIWindow(c)
#t.start_trials(10)
win.set_fullscreen()
runTouchApp()
