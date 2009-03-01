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
from pymt.ui import colors

class MTSlider(MTWidget):
    '''MTSlider is an implementation of a scrollbar using MTWidget.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `orientation` : str, default is vertical
            Type of orientation, can be 'horizontal' or 'vertical'
        `value` : int, default is `min`
            Default value of slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('padding', 8)
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('color', colors.selected)
        kwargs.setdefault('bgcolor', colors.background)
        kwargs.setdefault('size', (30, 400))
        kwargs.setdefault('value', None)

        super(MTSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts    = [] # only react to touch input that originated on this widget
        self.orientation      = kwargs.get('orientation')
        self.padding        = kwargs.get('padding')
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')
        self._value         = self.min
        if kwargs.get('value'):
            self._value = kwargs.get('value')

    def on_value_change(self, value):
        pass

    def set_value(self, _value):
        self._value = _value
        self.dispatch_event('on_value_change', self._value)
    def get_value(self):
        return self._value
    value = property(get_value, set_value, doc='Value of the slider')

    def draw(self):
        with gx_blending:
            x,y,w,h = self.x, self.y, self.width, self.height
            p2 =self.padding/2
            # draw outer rectangle
            glColor4f(*self.bgcolor)
            drawRectangle(pos=(x,y), size=(w,h))
            # draw inner rectangle
            glColor4f(*self.color)
            if self.orientation == 'vertical':
                length = int((self._value - self.min) * (self.height - self.padding) / (self.max - self.min))
                drawRectangle(pos=(x+p2,y+p2), size=(w - self.padding, length))
            else:
                length = int((self._value - self.min) * (self.width - self.padding) / (self.max - self.min))
                drawRectangle(pos=(x+p2,y+p2), size=(length, h - self.padding))

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.touchstarts.append(touchID)
            self.on_touch_move(touches, touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            last_value = self._value
            if self.orientation == 'vertical':
                self._value = (y - self.y) * (self.max - self.min) / float(self.height) + self.min
            else:
                self._value = (x - self.x) * (self.max - self.min) / float(self.width) + self.min
            if self._value >= self.max:
                self._value = self.max
            if self._value <= self.min:
                self._value = self.min
            if not self._value == last_value:
                self.dispatch_event('on_value_change', self._value)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)

class MT2DSlider(MTWidget):
    '''MT2DSlider is an implementation of a 2D slider using MTWidget.

    :Parameters:
        `min_x` : int, default is 20
            Minimum value of slider
        `max_x` : int, default is 100
            Maximum value of slider
        `min_y` : int, default is 20
            Minimum value of slider
        `max_y` : int, default is 100
            Maximum value of slider
        `radius` : int, default is 200
            Radius of the slider handle
        `value_x` : int, default is `min_x`
            Default X value of slider
        `value_y` : int, default is `min_y`
            Default Y value of slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min_x', 20)
        kwargs.setdefault('max_x', 100)
        kwargs.setdefault('min_y', 20)
        kwargs.setdefault('max_y', 100)
        kwargs.setdefault('radius', 20)
        kwargs.setdefault('size', (200, 200))
        kwargs.setdefault('value_x', None)
        kwargs.setdefault('value_y', None)
        kwargs.setdefault('color', colors.selected)
        kwargs.setdefault('bgcolor', colors.background)

        super(MT2DSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.radius     = kwargs.get('radius')
        self.padding    = kwargs.get('radius')
        self.min_x      = kwargs.get('min_x')
        self.max_x      = kwargs.get('max_x')
        self.min_y      = kwargs.get('min_y')
        self.max_y      = kwargs.get('max_y')
        self.radius     = kwargs.get('radius')
        self._value_x, self._value_y = self.min_x, self.min_y
        if kwargs.get('value_x'):
            self._value_x = kwargs.get('value_x')
        if kwargs.get('value_y'):
            self._value_y = kwargs.get('value_y')

    def on_value_change(self, value_x, value_y):
        pass

    def set_value_x(self, value):
        self._value_x = value
        self.dispatch_event('on_value_change', self._value_x, self._value_y)
        self.draw()

    def get_value_x(self):
        return self._value_x

    value_x = property(get_value_x, set_value_x, doc='Value of the slider (x axis)')

    def set_value_y(self, value):
        self._value_y = value
        self.dispatch_event('on_value_change', self._value_x, self._value_y)
        self.draw()

    def get_value_y(self):
        return self._value_y

    value_y = property(get_value_y, set_value_y, doc='Value of the slider (y axis)')

    def draw(self):
        with gx_blending:
            x,y,w,h = self.x,self.y,self.width, self.height
            # draw outer rectangle
            glColor4f(*self.bgcolor)
            drawRectangle(pos=(x,y), size=(w,h))
            # draw inner circle
            glColor4f(*self.color)
            pos_x = int((self._value_x - self.min_x) * (self.width - self.padding*2) / (self.max_x - self.min_x))  + self.x + self.padding
            pos_y = int((self._value_y - self.min_y) * (self.height - self.padding*2) / (self.max_y - self.min_y)) + self.y + self.padding
            drawCircle(pos=(pos_x, pos_y), radius = self.radius)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.touchstarts.append(touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            last_value_x, last_value_y = self._value_x, self._value_y
            self._value_x = (x - self.x) * (self.max_x - self.min_x) / float(self.width) + self.min_x
            self._value_y = (y - self.y) * (self.max_y - self.min_y) / float(self.height) + self.min_y
            if self._value_x >= self.max_x:
                self._value_x = self.max_x
            if self._value_x <= self.min_x:
                self._value_x = self.min_x
            if self._value_y >= self.max_y:
                self._value_y = self.max_y
            if self._value_y <= self.min_y:
                self._value_y = self.min_y
            if not self._value_x == last_value_x or not self._value_y == last_value_y:
                self.dispatch_event('on_value_change', self._value_x, self._value_y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)

MTWidgetFactory.register('MT2DSlider', MT2DSlider)
MTWidgetFactory.register('MTSlider', MTSlider)
