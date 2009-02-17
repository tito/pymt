#!/usr/bin/env python

from pymt import *
import random
import math

class MTMultiSlider(MTWidget):
    def __init__(self, **kwargs):
        super(MTMultiSlider, self).__init__(**kwargs)
        kwargs.setdefault('sliders', 8)
        self._sliders = kwargs.get('sliders')
        self._slider_values = [random.random() for x in range(self._sliders)]
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
            
if __name__ == '__main__':
    w = MTWindow(fullscreen=False)
    wsize = w.size
    mms = MTMultiSlider(pos = (40,50), size = (450, 300), color = (1,0.5,0,1))
    w.add_widget(mms)
    runTouchApp()
    
        
        
        