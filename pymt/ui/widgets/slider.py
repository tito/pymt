'''
Slider package: provide multiple slider implementation (simple, xy, boundary...)
'''

from __future__ import with_statement, division
import random
__all__ = ['MTSlider', 'MTXYSlider', 'MTBoundarySlider']

from pyglet.gl import *
from ...graphx import drawRectangle, drawCircle, drawLabel, set_color
from ..factory import MTWidgetFactory
from widget import MTWidget

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
    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('padding', 8)
        kwargs.setdefault('orientation', 'vertical')
        if kwargs.get('orientation') == 'vertical':
            kwargs.setdefault('size', (30, 400))
        else:
            kwargs.setdefault('size', (400, 30))
        kwargs.setdefault('value', None)

        super(MTSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts    = [] # only react to touch input that originated on this widget
        self.orientation    = kwargs.get('orientation')
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
        x,y,w,h = self.x, self.y, self.width, self.height
        p2 =self.padding/2
        # draw outer rectangle
        set_color(*self.style.get('bg-color'))
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner rectangle
        set_color(*self.style.get('slider-color'))
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

class MTXYSlider(MTWidget):
    '''MTXYSlider is an implementation of a 2D slider using MTWidget.

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
    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider 
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

        super(MTXYSlider, self).__init__(**kwargs)
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
        x,y,w,h = self.x,self.y,self.width, self.height
        # draw outer rectangle
        set_color(*self.style.get('bg-color'))
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner circle
        set_color(*self.style.get('slider-color'))
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

class MTBoundarySlider(MTWidget):
    '''MTBoundarySlider is a widget that allows you to select minimum and maximum values.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `orientation` : str, default is vertical
            Type of orientation, can be 'horizontal' or 'vertical'
        `value_max` : int, default is `max - (max/4)`
            The default maximum value
        `value_min` : int, the default is `min + (max/4)`
            The default minumum value
        `showtext` : boolean, defaults to false
            If true, the widget will show the min/max value

    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('showtext', False)
        if kwargs.get('orientation') == 'vertical':
            kwargs.setdefault('size', (30, 400))
        else:
            kwargs.setdefault('size', (400, 30))

        super(MTBoundarySlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts    = [] # only react to touch input that originated on this widget
        self.orientation    = kwargs.get('orientation')
        self.padding        = kwargs.get('padding')
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')
        self.showtext = kwargs.get('showtext')

        kwargs.setdefault('value_max', 1)
        kwargs.setdefault('value_min', self.max/2)
        self.value_max = kwargs.get('value_max')
        self.value_min = kwargs.get('value_min')

    def get_value(self):
        '''Scale the value to the minimum and maximum system set by the user
        '''
        if self.orientation == 'vertical':
            tmin = (self.value_min / self.height) * self.max
            tmax = (self.value_max / self.height) * self.max
        elif self.orientation == 'horizontal':
            tmin = (self.value_min / self.width) * self.max
            tmax = (self.value_max / self.width) * self.max

        return tmin, tmax

    def on_value_change(self, min, max):
        '''Event prototype'''
        pass

    def draw(self):
        x, y, w, h = self.x, self.y, self.width, self.height
        #Draw the outer rectangle(border)
        set_color(*self.get('bg-color'))
        drawRectangle(pos=(x, y), size=(w,h))
        #Draw the slider
        set_color(*self.get('slider-color'))
        if self.orientation == 'vertical':
            drawRectangle(pos=(self.x, self.y + self.value_min), size=(w, self.value_max-self.value_min))
            if self.showtext:
                drawLabel(str(self.value_min), pos=(self.x+self.width/2, self.y+self.value_min+10), font_size=16)
                drawLabel(str(self.value_max), pos=(self.x+self.width/2, self.y+self.value_max-10), font_size=16)
        elif self.orientation == 'horizontal':
            drawRectangle(pos=(self.x + self.value_min, self.y), size=(self.value_max - self.value_min, h))

    def on_touch_down(self, touches, touchID, x, y):
        touches[touchID].oxpos = x  #So the first on_touch_move in a two-finger-drag doesn't teleport the widget
        touches[touchID].oypos = y  #Ditto ^
        if self.collide_point(x,y):
            if touches[touchID].is_double_tap:
                #Randomize the bound
                if self.orientation == 'vertical':
                    self.value_min = random.randrange(0, self.height)
                    self.value_max = random.randrange(self.value_min, self.height)
                else:
                    self.value_min = random.randrange(0, self.width)
                    self.value_max = random.randrange(self.value_min, self.width)
            #Decide wether we will move the upper or lower bound
            if self.orientation == 'vertical':
                if y < (self.value_min + self.y*2 + self.value_max)/2:
                    touches[touchID].side = 'value_min'
                else:
                    touches[touchID].side = 'value_max'
            elif self.orientation == 'horizontal':
                if x < (self.value_min + self.x*2 + self.value_max)/2:
                    touches[touchID].side = 'value_min'
                else:
                    touches[touchID].side = 'value_max'

            self.touchstarts.append(touchID)
            self.on_touch_move(touches, touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            #Either move a given bound, or shift both
            if self.orientation == 'vertical':
                if len(self.touchstarts) >= 2:
                    #Two or more fingers, shift the whole bound
                    rel = (y - touches[touchID].oypos)
                    self.value_min += rel
                    self.value_max += rel
                else:
                    #Only one, just change one bound
                    setattr(self, touches[touchID].side, y - self.y)
                    self.dispatch_event('on_value_change', *self.get_value())
            elif self.orientation == 'horizontal':
                if len(self.touchstarts) >= 2:
                    #Two or more fingers, shift the whole bound
                    rel = (x - touches[touchID].oxpos)
                    self.value_min += rel
                    self.value_max += rel
                else:
                    #Only one, just change one bound
                    setattr(self, touches[touchID].side, x - self.x)
                    self.dispatch_event('on_value_change', *self.get_value())

        touches[touchID].oypos = y
        touches[touchID].oxpos = x

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)

MTWidgetFactory.register('MTXYSlider', MTXYSlider)
MTWidgetFactory.register('MTSlider', MTSlider)
MTWidgetFactory.register('MTBoundarySlider', MTBoundarySlider)
