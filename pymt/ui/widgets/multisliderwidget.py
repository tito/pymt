#!/usr/bin/env python
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.factory import MTWidgetFactory
from pymt.graphx import *

class MTMultiSlider(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('sliders', 20)
        kwargs.setdefault('color', (1,0.5,0,1))
        kwargs.setdefault('background_color', (0.2,0.2,0.2,0.5))
        kwargs.setdefault('size', (400,300))
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('init_value', 0.5)
        super(MTMultiSlider, self).__init__(**kwargs)   

        self.register_event_type('on_value_change')
        self._sliders = kwargs.get('sliders')
        self._spacing = kwargs.get('spacing')
        self._background_color = kwargs.get('background_color')
        self.slider_values = [kwargs.get('init_value') for x in range(self._sliders)]        
        
    def draw(self):
        # Draw background
        glColor4f(*self._background_color)
        drawRectangle(pos=(self.x,self.y), size=(self.width,self.height))
        # Draw sliders
        glColor4f(*self.color)
        for slider in range(self._sliders):
            pos_x = self.x + slider * (float(self.width) / self._sliders)
            pos_y = self.y
            size_x = (float(self.width) / self._sliders) - self._spacing
            size_y = self.height * self.slider_values[slider]
            drawRectangle(pos = (pos_x, pos_y), size = (size_x, size_y))

    def on_value_change(self, value):
        pass
    
    def on_touch_down(self, touches, touchID, x, y):
        if x > self.x and x < self.x + self.width:
            current_slider = self.return_slider(x)
            last_value = self.slider_values[current_slider]
            self.slider_values[current_slider] = (y - self.y) / float(self.height)
            if self.slider_values[current_slider] >= 1:
                self.slider_values[current_slider] = 1
            if self.slider_values[current_slider] <= 0:
                self.slider_values[current_slider] = 0
                
            if not self.slider_values[current_slider] == last_value:
                self.dispatch_event('on_value_change', self.slider_values)
        return True
        
    def on_touch_move(self, touches, touchID, x, y):
        self.on_touch_down(touches, touchID, x, y)
        
    def return_slider(self, x):
        return int((x - self.x) / float(self.width)  * self._sliders)
            
MTWidgetFactory.register('MTMultiSlider', MTMultiSlider)

if __name__ == '__main__':
    from pymt import *
    w = MTWindow(fullscreen=False)
    wsize = w.size
    mms = MTMultiSlider(pos = (20,20))
    w.add_widget(mms)
    runTouchApp()
    
        
        
        
