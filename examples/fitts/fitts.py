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
                
                
                
from numpy import *
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
                drawRectangle((-0.5, -0.5) ,(1, 1))
                glPopMatrix()

class TwoPointMappingTask(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)

                self.rotation = self._rotation = 0.0
                self.translation = self._translation = Vector(pos[0],pos[1])
                self.zoom = self._zoom = 1.0

                self.touchDict = {}                
                self.original_points = [Vector(0,0),Vector(0,0)]
                self.originalCenter = Vector(0,0)
                self.newCenter = Vector(0,0)
                
                
        
        def draw(self):
                glPushMatrix()
                glTranslatef(self.translation[0], self.translation[1], 0)
                glRotatef(-1.0*self.rotation*18 , 0, 0, 1)
                glScalef(self.zoom, self.zoom, 1)
                glScalef(self.width, self.height, 1)
                drawRectangle((-0.5, -0.5) ,(1, 1))
                glPopMatrix()
        

                
        def getAngle(self, x,y):
                        if (x == 0.0):
                                if(y < 0.0):  return 270
                                else:         return 90
                        elif (y == 0):
                                if(x < 0):  return 180
                                else:       return 0
                        if ( y > 0.0):
                                if (x > 0.0): return math.atan(y/x) * math.pi
                                else:         return 180.0-math.atan(y/-x) * math.pi
                        else:
                                if (x > 0.0): return 360.0-math.atan(-y/x) * math.pi
                                else:         return 180.0+math.atan(-y/-x) * math.pi
                
		
	def on_touch_down(self, touches, touchID, x, y):
                if len(self.touchDict) < 2:
                        v = Vector(x,y)
                        self.original_points[len(self.touchDict)] = v
                        self.touchDict[touchID] = v
                        
     
                

	def on_touch_move(self, touches, touchID, x, y):                
                print self.touchDict
                if len(self.touchDict) == 1 and touchID in self.touchDict:
                        self.translation = Vector(x,y) - self.original_points[0] + self._translation
                        
                if len(self.touchDict) == 2 and touchID in self.touchDict:
                        points = self.touchDict.values()                       

                        #scale
                        distOld = Distance(self.original_points[0], self.original_points[1])
                        distNew = Distance(points[0], points[1])
                        self.zoom = distNew/distOld * self._zoom
                
                        #translate
                        self.originalCenter = self.original_points[0] + (self.original_points[1] - self.original_points[0])*0.5
                        self.newCenter = points[0] + (points[1] - points[0])*0.5
                        self.translation = (self.newCenter - self.originalCenter)  + self._translation
                       
                        #rotate
                        v1 = self.original_points[1] - self.original_points[0]
                        v2 =   points[0] - points[1]
                        self.rotation =  self.getAngle(v1[0], v1[1]) - self.getAngle(v2[0], v2[1]) + self._rotation
                        

                if touchID in self.touchDict:
                        self.touchDict[touchID] = Vector(x,y)
                
                         
	def on_touch_up(self, touches, touchID, x, y):
                if touchID in self.touchDict: #end interaction 
                        self._zoom = self.zoom
                        self._translation += self.translation - self._translation
                        self._rotation += self.rotation - self._rotation
                        self.touchDict = {}
                
                
c = Container()
c.add_widget( TwoPointMappingTask(pos=(300,300))  )
c.add_widget( Target(pos=(700,500)) )
win = UIWindow(c)
#t.start_trials(10)
#win.set_fullscreen()
runTouchApp()