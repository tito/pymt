#!/usr/bin/env python

from pymt import *
import random
import math

class MTMultiSlider(MTWidget):
    def __init__(self, **kwargs):
        super(MTMultiSlider, self).__init__(**kwargs)
        kwargs.setdefault('sliders', 27)
        self._sliders = kwargs.get('sliders')
        #self._slider_values = [random.random() for x in range(self._sliders)]
        self._slider_values = [0.5 for x in range(self._sliders)]
        self._spacing = 2
    
    def draw(self):
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(self.x,self.y), size=(self.width,self.height))
        glColor4f(*self.color)
        for slider in range(self._sliders):
            pos_x = self.x + slider * (float(self.width) / self._sliders)
            pos_y = self.y
            size_x = (float(self.width) / self._sliders) - self._spacing
            size_y = self.height * self._slider_values[slider]
            drawRectangle(pos = (pos_x, pos_y), size = (size_x, size_y))

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            print self.return_slider(x)
            self._slider_values[self.return_slider(x)] = (y - self.y) / float(self.height)
            return True
        
    def on_touch_move(self, touches, touchID, x, y):
        self.on_touch_down(touches, touchID, x, y)
        
    def return_slider(self, x):
        return int((x - self.x) / float(self.width)  * self._sliders)
            
if __name__ == '__main__':
    w = MTWindow(fullscreen=False)
    wsize = w.size
    mms = MTMultiSlider(pos = (40,50), size = (450, 300), color = (1,0.5,0,1))
    w.add_widget(mms)
    runTouchApp()
    
        
        
        