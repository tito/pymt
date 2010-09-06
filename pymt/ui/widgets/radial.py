'''
Vector slider: a radial slider that provide vector manipulation
'''

from __future__ import division

__all__ = ('MTVectorSlider', )

from OpenGL.GL import GL_POLYGON, glVertex2f
from math import cos, sin, sqrt, degrees, atan, radians
from pymt.graphx import drawCircle, set_color, gx_begin
from pymt.vector import Vector
from pymt.ui.widgets.widget import MTWidget

def _get_distance(Pos1, Pos2):
    '''Get the linear distance between two points'''
    return sqrt((Pos2[0] - Pos1[0])**2 + (Pos2[1] - Pos1[1])**2)

def prot(p, d, rp=(0, 0)):
    '''Rotates a given point(p) d degrees counter-clockwise around rp'''
    d = -radians(d)
    p = list(p)
    p[0] -= rp[0]
    p[1] -= rp[1]
    np = [p[0]*cos(d) + p[1]*sin(d), -p[0]*sin(d) + p[1]*cos(d)]
    np[0] += rp[0]
    np[1] += rp[1]
    return tuple(np)

class MTVectorSlider(MTWidget):
    '''
    This is a slider that provides an arrow, and allows you to manipulate
    it just like any other vector, adjusting its angle and amplitude.

    :Parameters:
        `radius` : int, default to 200
            The radius of the whole widget

    :Events:
        `on_amplitude_change`: (amplitude)
            Fired when amplitude is changed
        `on_angle_change`: (angle)
            Fired when angle is changed
        `on_vector_change`: (amplitude, angle)
            Fired when vector is changed

    :Styles:
        `vector-color` : color
            Color of the vector
        `slider-color` : color
            Color of the triangle
        `bg-color` : color
            Background color of the slider
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('radius', 200)

        super(MTVectorSlider, self).__init__(**kwargs)

        self.radius = kwargs.get('radius')

        self.vector = Vector(self.x+self.radius, self.y)
        self.amplitude = 0
        self.angle = 0

        self.register_event_type('on_amplitude_change')
        self.register_event_type('on_angle_change')
        self.register_event_type('on_vector_change')

    def on_amplitude_change(self, *largs):
        pass

    def on_angle_change(self, *largs):
        pass

    def on_vector_change(self, *largs):
        pass

    def collide_point(self, x, y):
        '''Because this widget is a circle, and this method as
        defined in MTWidget is for a square, we have to override
        it.'''
        return _get_distance(self.pos, (x, y)) <= self.radius

    def _calc_stuff(self):
        '''Recalculated the args for the callbacks'''
        self.amplitude = self.vector.distance(self.pos)
        # Make a new vector relative to the origin
        tvec = [self.vector[0], self.vector[1]]
        tvec[0] -= self.pos[0]
        tvec[1] -= self.pos[1]

        # Incase python throws float div or div by zero exception,
        # ignore them, we will be close enough
        try:
            self.angle = degrees(atan((int(tvec[1])/int(tvec[0]))))
        except Exception:
            pass

        # Ajdust quadrants so we have 0-360 degrees
        if tvec[0] < 0 and tvec[1] > 0:
            self.angle = 90 + (90 + self.angle)
        elif tvec[0] < 0 and tvec[1] < 0:
            self.angle += 180
        elif tvec[0] > 0 and tvec[1] < 0:
            self.angle = 270 + (self.angle + 90)
        elif tvec[0] > 0 and tvec[1] > 0:
            pass

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.vector[0], self.vector[1] = touch.x, touch.y
            self._calc_stuff()

            self.dispatch_event('on_aplitude_change', self.amplitude)
            self.dispatch_event('on_angle_change', self.angle)
            self.dispatch_event('on_vector_change', self.amplitude, self.angle)

            return True
    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.vector[0], self.vector[1] = touch.x, touch.y
            self._calc_stuff()

            self.dispatch_event('on_aplitude_change', self.amplitude)
            self.dispatch_event('on_angle_change', self.angle)
            self.dispatch_event('on_vector_change', self.amplitude, self.angle)

            return True

    def draw(self):
        # Background
        set_color(*self.style.get('bg-color'))
        drawCircle(self.pos, self.radius)

        # A good size for the hand, proportional to the size of the widget
        hd = self.radius / 10
        # Draw center of the hand
        set_color(*self.style.get('vector-color'))
        drawCircle(self.pos, hd)
        # Rotate the triangle so its not skewed
        l = prot((self.pos[0] - hd, self.pos[1]), self.angle-90, self.pos)
        h = prot((self.pos[0] + hd, self.pos[1]), self.angle-90, self.pos)
        # Draw triable of the hand
        with gx_begin(GL_POLYGON):
            glVertex2f(*l)
            glVertex2f(*h)
            glVertex2f(self.vector[0], self.vector[1])

if __name__ == '__main__':
    def on_vector_change(amp, ang):
        print amp, ang

    from pymt import MTWindow, runTouchApp
    w = MTWindow(fullscreen=False)
    mms = MTVectorSlider(pos=(200, 200))
    mms.push_handlers('on_vector_change', on_vector_change)
    w.add_widget(mms)
    runTouchApp()
