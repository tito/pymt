#!/usr/bin/env python

from pymt import *
from pyglet import *
from pyglet.gl import *

import pickle, pprint


class ControlDialog(DragableWidget):
    def __init__(self, text, parent):
        DragableWidget.__init__(self,parent, size = (400,600))
        self.label = pyglet.text.Label(text ,x=200, y= 900)
        
    def draw(self):
        drawRectangle((self.x, self.y) ,(self.width, self.height), color=(0.3,0.2,0.2))
        self.label.x, self.label.y = (self.x +10, self.y + 580)
        self.label.draw()

class Plot(DragableWidget):
    def __init__(self, function, parent):
        DragableWidget.__init__(self,parent, size = (800,600))
        self.function = function
        
        
    def draw(self):
        drawRectangle((self.x, self.y) ,(self.width, self.height), color=(0.2,0.2,0.2))
        self.draw_grid()
    
    def draw_grid(self):
        x, y = self.x + 40, self.y + 40
        w, h = self.width -60, self.height -60
        drawLine( (x,y,x+w,y) )
        drawLine( (x,y,x,y+h) )
        for size in self.function:
            x,y,s = self.x  + size*5 - 100, self.y+ 40 +self.function[size][0]*5,  self.function[size][1]
            drawCircle(pos=(x,y), scale = 0.001 *s )
    
class DataViewer(Container):
    def __init__(self, data_file, parent=None):
        Container.__init__(self, parent=parent)
        self.data_file = data_file
        
        pkl_file = open(data_file, 'rb')
        self.data = pickle.load(pkl_file)
             
        self.widgets.append(Plot(self.size_vs_speed(), self) )
        
        caption = "Number of total records: " + str(len(self.data))
        self.widgets.append(ControlDialog(caption,self))
     
    def size_vs_speed(self):
        function = {}
        for trial in self.data[1:]:
            duration, x, y, size, distance_to_last_point, errors = trial
            function[size] = [duration, distance_to_last_point]
        return function
     

        


        

       
w = UIWindow(DataViewer('data.pkl'))
w.set_fullscreen()
runTouchApp()