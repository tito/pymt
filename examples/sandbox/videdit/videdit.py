#!/usr/bin/env python
# coding: utf-8

# This is a work in progress please do not modify, thanks - Nathanaël Lécaudé

from pymt import *

class Timeline(MTScatterPlane):
    def __init__(self, **kwargs):
        super(Timeline,self).__init__( **kwargs)

class Event(MTWidget):
    def __init__(self, **kwargs):
        super(Event,self).__init__(**kwargs)
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.mode = 'move'
        
    def draw(self):
        set_color(1,0,1,1)
        drawRectangle(size = self.size, pos = self.pos)
        
    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y):
            self.touchstarts.append(touch.id)
            self.first_x = touch.x
            self.first_y = touch.y
            self.first_pos_x = self.x
            self.first_pos_y = self.y
            self.first_width = self.width
            if touch.x > self.x + self.width - 30:
                self.mode = 'trim_end'
            if touch.x < self.x + 30:
                self.mode = 'trim_start'
            return True
        
    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            delta_x = touch.x - self.first_x
            delta_y = touch.y - self.first_y
            if self.mode == 'move':
                self.x = self.first_pos_x + delta_x
                self.y = self.first_pos_y + delta_y
            if self.mode == 'trim_end':
                self.width = self.first_width + delta_x
            if self.mode == 'trim_start':
                self.x = self.first_pos_x + delta_x
                self.width = self.first_width - delta_x
            return True
            
    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
            self.mode = 'move'
            return True
        
        
        
w = MTWindow(style = {'bg-color': (0,0,0,1)})
e = Event(size = (400,100))
e2 = Event(pos=(400,400), size = (300,100))
t = Timeline(do_rotation = False)

t.add_widget(e)
t.add_widget(e2)
w.add_widget(t)
runTouchApp()
