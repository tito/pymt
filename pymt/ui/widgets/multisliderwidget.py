#!/usr/bin/env python
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget
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
        self._init_value = kwargs.get('init_value')
        self.slider_values = [self._init_value for x in range(self._sliders)]
        
    def _get_background_color(self):
        return self._background_color
    def _set_background_color(self, bckcolor):
        self._background_color = bckcolor
    background_color = property(_get_background_color, _set_background_color)
    
    def _get_sliders(self):
        return self._sliders
    def _set_sliders(self, quantity):
        if quantity < self._sliders:
            self.slider_values = self.slider_values[0:quantity]
            self._sliders = quantity
        if quantity > self._sliders:
            self.slider_values = self.slider_values + list([self._init_value for x in range(quantity - self._sliders)])
            self._sliders = quantity
        else:
            return
    sliders = property(_get_sliders, _set_sliders)
    
    def _get_spacing(self):
        return self._background_color
    def _set_spacing(self, spacing):
        self._spacing = spacing
    spacing = property(_get_spacing, _set_spacing)
    
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
    w = MTWindow()
    widgets = []
    keyb = MTTextInput(size = (35,30), font_size = 20)
    @keyb.event
    def on_text_validate():
        exec keyb.label
        keyb.label = ''
        keyb.size = (35,30)
    mms = MTMultiSlider(pos = (40,40))
    w.add_widget(mms)
    w.add_widget(keyb)
    runTouchApp()
    
        
        
        
