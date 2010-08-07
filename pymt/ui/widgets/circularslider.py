'''
Circular Slider: Using this you can make circularly shaped sliders
'''


__all__ = ('MTCircularSlider', 'RangeException')

from OpenGL.GL import glTranslatef, glRotatef
from pymt.graphx import drawSemiCircle, gx_matrix, set_color
from pymt.vector import Vector
from pymt.ui.widgets.widget import MTWidget
from math import cos, sin, radians

class RangeException(Exception):
    pass

class MTCircularSlider(MTWidget):
    '''MTCircularSlider is an implementation of a circular scrollbar using
    MTWidget.

    .. warning::
        The widget is drawed from his center. Cause of that, the size of the
        widget will be automaticly adjusted from the radius of the slider.
        Eg: if you ask for a radius=100, the widget size will be 200x200

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
        `radius` : int, default is 200
            Radius of the slider
        `rotation` : int, default is 0
            Start rotation of circle
        `padding` : int
            Padding of content

    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider

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
        kwargs.setdefault('rotation', 0)

        have_size = 'size' in kwargs

        super(MTCircularSlider, self).__init__(**kwargs)

        # register event
        self.register_event_type('on_value_change')

        # privates
        self._last_touch    = (0, 0)
        self._slider_angle  = 0.

        self.radius         = kwargs.get('radius')
        self.rotation       = kwargs.get('rotation')
        self.thickness      = kwargs.get('thickness')
        self.padding        = kwargs.get('padding')
        self.sweep_angle    = kwargs.get('sweep_angle')
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')

        # calculate radius line, needed for collision
        self._radius_line   = self.radius * sin(radians(self.rotation)), \
                              self.radius * cos(radians(self.rotation))

        # adjust size
        if not have_size:
            self.size       = self.radius * 2, self.radius * 2

        # set value
        self._value         = 0
        self.value          = self.min
        if kwargs.get('value'):
            self.value      = kwargs.get('value')

    def collide_point(self, x, y):
        #A algorithm to find the whether a touch is within a semi ring
        cx, cy = self.center
        point_dist = Vector(self.center).distance((x, y))
        point_angle = Vector(self._radius_line).angle((x - cx, y - cy))
        if point_angle < 0:
            point_angle = 360. + point_angle
        if 0 < point_angle > self.sweep_angle:
            return False
        return self.radius - self.thickness < point_dist <= self.radius

    def on_value_change(self, value):
        pass

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.userdata['pymt.circularslider'] = self
            self._calculate_angle(*touch.pos)
            return True

    def on_touch_move(self, touch):
        if touch.userdata.get('pymt.circularslider') is self:
            self._calculate_angle(*touch.pos)
            return True

    def _calculate_angle(self, x, y):
        cx, cy = self.center
        self._last_touch = x - cx, y - cy 
        angle = Vector(self._radius_line).angle(self._last_touch)
        if angle < 0:
            angle += 360
        try:
            self.value = angle * (self.max - self.min) / \
                         self.sweep_angle + self.min
            self._slider_angle = angle
        except RangeException:
            pass
        self.dispatch_event('on_value_change', self._value)

    def draw(self):
        super(MTCircularSlider, self).draw()

        # faster calculation if we remove dot
        x, y = self.center
        p = 0, 0
        r = self.radius
        t = self.thickness
        s = self.sweep_angle
        padding = self.padding

        with gx_matrix:
            set_color(*self.style.get('bg-color'))
            glTranslatef(x, y, 0)
            glRotatef(-self.rotation, 0, 0, 1)
            drawSemiCircle(p, r - t, r, 32, 1, 0, s)
            set_color(*self.style.get('slider-color'))
            drawSemiCircle(p, r - t + padding, r - padding,
                           32, 1, 0, self._slider_angle)

    def _get_value(self):
        return self._value
    def _set_value(self, value):
        value = float(value)
        if self.min < value > self.max:
            raise RangeException('Invalid value, not in range min/max')
        self._slider_angle = value / 100. * self.sweep_angle
        self._value = value / 100. * self.max
    value = property(_get_value, _set_value,
        doc='Sets the current value of the slider')
