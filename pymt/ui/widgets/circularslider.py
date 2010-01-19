'''
Circular Slider: Using this you can make circularly shaped sliders
'''


__all__ = ['MTCircularSlider']

from OpenGL.GL import *
from ...graphx import drawSemiCircle, gx_matrix_identity, set_color
from ...vector import Vector
from ..factory import MTWidgetFactory
from widget import MTWidget
from math import cos,sin,radians

class MTCircularSlider(MTWidget):
    '''MTCircularSlider is an implementation of a circular scrollbar using MTWidget.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `sweep_angle` : int, default is 90
            The anglular length of the slider you want.
        `value` : int, default is `min`
            Default value of slider
        `thickness` : int, default is 40
            Thickness of the slider
        `Radius` : int, default is 200
            Radius of the slider
    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider
        `padding` : int
            Padding of content

    :Events:
        `on_value_change`
            Fired when slider value is changed
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('radius', 200)
        kwargs.setdefault('thickness', 40)
        kwargs.setdefault('padding', 3)
        kwargs.setdefault('sweep_angle', 90)
        super(MTCircularSlider, self).__init__(**kwargs)
        self.radius = kwargs.get('radius')
        self.last_touch = (0, 0)
        self.angle = 0.0
        self.rotation = kwargs.get('rotation')
        self.radius_line = (int(self.radius*sin(radians(self.rotation))),int(self.radius*cos(radians(self.rotation))))
        self.thickness = kwargs.get('thickness')
        self.padding = kwargs.get('padding')
        self.sweep_angle = kwargs.get('sweep_angle')
        self.slider_fill_angle = 0.0
        self.slider_color = kwargs.get('slider_color')
        self.register_event_type('on_value_change')
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')
        self._value         = self.min
        if kwargs.get('value'):
            self._value = kwargs.get('value')
        self.touchstarts    = []

    def collide_point(self, x, y):
        #A algorithm to find the whether a touch is within a semi ring
        point_dist = Vector(self.pos).distance((x, y))
        point_angle = Vector(self.radius_line).angle((x - self.pos[0], y - self.pos[1]))
        if point_angle < 0:
           point_angle=360+point_angle
        if point_angle <= self.sweep_angle and point_angle >=0:
            return  point_dist<= self.radius and point_dist > self.radius-self.thickness

    def on_value_change(self, value):
        pass

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchstarts.append(touch.id)
            self.last_touch = (touch.x - self.pos[0], touch.y - self.pos[1])
            self._value = (self.slider_fill_angle) * (self.max - self.min) / self.sweep_angle + self.min
            self._calculate_angle()
            return True

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y) and touch.id in self.touchstarts:
            self.last_touch = (touch.x - self.pos[0], touch.y - self.pos[1])
            self._value = (self.slider_fill_angle) * (self.max - self.min) / self.sweep_angle + self.min
            self._calculate_angle()
            return True

    def _calculate_angle(self):
        self.angle = Vector(self.radius_line).angle(self.last_touch)
        if self.angle<0:
            self.slider_fill_angle = self.angle+360
        else:
            self.slider_fill_angle = self.angle
        self.dispatch_event('on_value_change', self._value)

    def on_draw(self):
        with gx_matrix_identity:
            set_color(*self.style.get('bg-color'))
            glTranslated(self.pos[0], self.pos[1], 0)
            glRotatef(-self.rotation, 0, 0, 1)
            drawSemiCircle((0,0),self.radius-self.thickness,self.radius,32,1,0,self.sweep_angle)
            set_color(*self.style.get('slider-color'))
            drawSemiCircle((0,0),self.radius-self.thickness+self.padding,self.radius-self.padding,32,1,0,self.slider_fill_angle)

    def _get_value(self,value):
        return self._value
    def _set_value(self,value):
        self.slider_fill_angle = float(value)/float(100)*self.sweep_angle
        self._value = float(value)/float(100)*self.max
        self._calculate_angle()
    value = property(_get_value, _set_value, doc='Sets the current value of the slider')

MTWidgetFactory.register('MTCircularSlider', MTCircularSlider)