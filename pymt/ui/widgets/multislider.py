'''
Multislider: a multi slider implementation
'''

__all__ = ['MTMultiSlider']

from ...graphx import set_color, drawRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTMultiSlider(MTWidget):
    '''Multi slider widget look like an equalizer widget.

    :Parameters:
        `sliders` : int, default to 20
            Number of sliders
        `spacing` : int, default to 1
            Spacing between slider
        `init_value` : float, default to 0.5
            Start value of all sliders

    :Styles:
        `slider-color` : color
            Color of slider
        `bg-color` : color
            Background color of slider

    :Events:
        `on_value_change` (int value)
            Fired when the value of one slider change

    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('sliders', 20)
        kwargs.setdefault('size', (400,300))
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('init_value', 0.5)
        super(MTMultiSlider, self).__init__(**kwargs)

        self.register_event_type('on_value_change')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self._sliders = kwargs.get('sliders')
        self._spacing = kwargs.get('spacing')
        self._init_value = kwargs.get('init_value')
        self.slider_values = [self._init_value for x in range(self._sliders)]

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
    sliders = property(_get_sliders, _set_sliders,
                       doc='Get/set the number of sliders')

    def _get_spacing(self):
        return self._spacing
    def _set_spacing(self, spacing):
        self._spacing = spacing
    spacing = property(_get_spacing, _set_spacing)

    def draw(self):
        # Draw background
        set_color(*self.style.get('bg-color'))
        drawRectangle(pos=(self.x,self.y), size=(self.width,self.height))
        # Draw sliders
        set_color(*self.style.get('slider-color'))
        for slider in range(self._sliders):
            pos_x = self.x + slider * (float(self.width) / self._sliders)
            pos_y = self.y
            size_x = (float(self.width) / self._sliders) - self._spacing
            size_y = self.height * self.slider_values[slider]
            drawRectangle(pos = (pos_x, pos_y), size = (size_x, size_y))

    def on_value_change(self, value):
        pass

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchstarts.append(touch.id)
            self.on_touch_move(touch)
            return True

    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            if touch.x > self.x and touch.x < self.x + self.width:
                current_slider = self.return_slider(touch.x)
                last_value = self.slider_values[current_slider]
                self.slider_values[current_slider] = (touch.y - self.y) / float(self.height)
                if self.slider_values[current_slider] >= 1:
                    self.slider_values[current_slider] = 1
                if self.slider_values[current_slider] <= 0:
                    self.slider_values[current_slider] = 0

                if not self.slider_values[current_slider] == last_value:
                    self.dispatch_event('on_value_change', self.slider_values)
            return True

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)

    def return_slider(self, x):
        return int((x - self.x) / float(self.width)  * self._sliders)

MTWidgetFactory.register('MTMultiSlider', MTMultiSlider)

if __name__ == '__main__':
    from pymt import *
    w = MTWindow()
    mms = MTMultiSlider(pos = (40,40))
    w.add_widget(mms)
    runTouchApp()
