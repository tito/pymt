#!/usr/bin/env python

from pymt import *

class Symbol(ZoomableWidget):
    def __init__(self, pos=(0,0), size=(150,100), text="Flowchart Symbol", color=GREEN):
        ZoomableWidget.__init__(self, pos=pos, size=size)
        self.color=color
        self.label = label = pyglet.text.Label(text,
                          font_name='Times New Roman',
                          font_size=32,
                          x=pos[0],y=pos[1],
                          anchor_x='center', anchor_y='center')


    def drawLabel(self):
        glPushMatrix()
	s = self.width *0.002
        glTranslatef(self.translation[0], self.translation[1], 0.0)
        glScalef(s,s,1.0)
        self.label.draw()
	glPopMatrix()

        
class Box(Symbol):
    def draw(self):
        x,y =self.translation[0]-self.width/2, self.translation[1]-self.height/2
        drawRectangle((x,y), (self.width, self.height), self.color)

        self.drawLabel()

class Rhombus(Symbol):
    def draw(self):
        x,y = self.translation[0], self.translation[1]
        drawTriangle((x,y), self.width, self.height/2, self.color)
        drawTriangle((x,y), self.width, -self.height/2, self.color)
        self.drawLabel()

class Oval(Symbol):
    def draw(self):
        x,y = self.translation[0], self.translation[1]
        glPushMatrix()
        glTranslatef(x,y,0)
        glScalef(1.0, float(self.height)/self.width, 1.0)
        drawCircle((0,0), radius=self.width/2.1, color=self.color)
        glPopMatrix()
        self.drawLabel()
              
    

    
w = Oval(size=(400,100) ,color=(1.0,0.0,0.0))
win = UIWindow(w)
#win.set_fullscreen()
runTouchApp()