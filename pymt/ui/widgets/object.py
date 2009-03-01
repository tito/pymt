from __future__ import with_statement
from pyglet import *
from pyglet.gl import *
from pymt.graphx import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget
from pymt.lib import squirtle
from pymt.vector import *
from pymt.logger import pymt_logger

class MTObjectWidget(MTWidget):
    '''MTObjectWidget is a widget who draw an object on table'''
    def __init__(self, **kwargs):
        super(MTObjectWidget, self).__init__(**kwargs)
        self.state      = ('normal', None)
        self.visible    = False
        self.angle      = 0
        self.id         = 0

    def on_object_down(self, touches, touchID,id, x, y,angle):
        self.x ,self.y  = x, y
        self.angle      = angle/pi*180
        self.visible    = True
        self.id         = id
        self.state      = ('dragging', touchID, x, y)
        return True

    def on_object_move(self, touches, touchID, id, x, y, angle):
        if self.state[0] == 'dragging' and self.state[1] == touchID:
            self.angle      = -angle/pi*180
            self.x, self.y  = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
            self.id         = id
            self.state      = ('dragging', touchID, x, y)
            return True

    def on_object_up(self, touches, touchID,id, x, y,angle):
        if self.state[1] == touchID:
            self.angle      = -angle/pi*180
            self.visible    = False
            self.id         = id
            self.state      = ('normal', None)
            return True

    def draw(self):
        if not self.visible:
            return
        with gx_matrix:
            glTranslatef(self.x,self.y,0.0)
            glRotatef(self.angle,0.0,0.0,1.0)
            glColor3f(1.0,1.0,1.0)
            drawRectangle((-0.5*self.width, -0.5*self.height) ,(self.width, self.height))
            glColor3f(0.0,0.0,1.0)
            with gx_begin(GL_LINES):
                glVertex2f(0.0,0.0)
                glVertex2f(0,-0.5*self.height)

MTWidgetFactory.register('MTObjectWidget', MTObjectWidget)
