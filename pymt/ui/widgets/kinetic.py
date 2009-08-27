'''
Kinetic: kinetic abstraction
'''

__all__ = ['MTKinetic']

from pyglet.gl import *
from ..factory import MTWidgetFactory
from ...input import Touch
from ...vector import Vector
from ...mtpyglet import getFrameDt, getAvailableTouchs
from stencilcontainer import MTStencilContainer
from widget import MTWidget

from pymt import *

class KineticTouch(Touch):
    counter = 0
    def __init__(self, args):
        KineticTouch.counter += 1
        id = 'kinetic%d' % KineticTouch.counter
        super(KineticTouch, self).__init__(id, args)
        self.mode = 'controlled'

    def depack(self, args):
        self.x, self.y = args
        if self.dxpos is not None:
            self.X = self.x - self.dxpos
            self.Y = self.y - self.dypos
        self.profile = 'xy'
        super(KineticTouch, self).depack(args)

class MTKinetic(MTWidget):
    '''Kinetic container.
    All widgets inside this container will have the kinetic applied
    to the touches. Kinetic is applied only if an children is touched
    on on_touch_down event.

    Kinetic will enter in the game when the on_touch_up append.
    Container will continue to send on_touch_move to children, until
    the velocity Vector is under `velstop` and sending on_touch_up ::

        from pymt import *
        k = MTKinetic()
        # theses widget will have kinetic movement
        k.add_widget(MTScatterSvg(filename='sun.svg'))
        k.add_widget(MTScatterSvg(filename='cloud.svg'))
        w = MTWindow()
        w.add_widget(k)
        runTouchApp()

    .. warning::
        In the on_touch_move/on_touch_up, the touchID will not exists in
        the touches arguments.

    :Parameters:
        `friction` : float, defaults to 10
            The Pseudo-friction of the pseudo-kinetic scrolling.
            Formula for friction is ::

                acceleration = 1 + friction * frame_delta_time

        `velstop` : float, default to 1.0
            The distance of velocity vector to stop animation
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('no_css', True)
        kwargs.setdefault('friction', 10)
        kwargs.setdefault('velstop', 1.0)
        super(MTKinetic, self).__init__(**kwargs)
        self.friction   = kwargs.get('friction')
        self.velstop    = kwargs.get('velstop')
        self.touch      = {} # internals

    def on_touch_down(self, touch):
        #This is a fix for a bug caused by more than one on_touch_down being sent for the same touch in a short period.
        if id(touch) in self.touch:
            oldktouch = self.touch[id(touch)]
            #put it in a new place on the list, and set it to be removed immediately.
            oldktouch.mode = 'spinning'
            oldktouch.X = -1.0
            oldktouch.Y = -1.0
            self.touch[oldktouch.id] = oldktouch

        # do a copy of the touch for kinetic
        args            = (touch.x, touch.y)
        ktouch          = KineticTouch(args)
        ktouch.userdata = touch.userdata
        ktouch.is_double_tap = touch.is_double_tap
        self.touch[id(touch)] = ktouch
        # grab the touch for not lost it !
        touch.grab(self)
        getAvailableTouchs().append(ktouch)
        # and dispatch !
        return super(MTKinetic, self).on_touch_down(ktouch)

    def on_touch_move(self, touch):
        if touch.grab_current != self:
            return
        if id(touch) not in self.touch:
            return
        ktouch = self.touch[id(touch)]
        ktouch.move([touch.x, touch.y])
        ktouch.userdata = touch.userdata
        ret = super(MTKinetic, self).on_touch_move(ktouch)

        # dispatch ktouch also in grab mode
        for wid in ktouch.grab_list:
            ktouch.push()
            ktouch.x, ktouch.y = self.to_window(*ktouch.pos)
            if wid.parent:
                ktouch.x, ktouch.y = wid.parent.to_widget(ktouch.x, ktouch.y)
            else:
                ktouch.x, ktouch.y = wid.to_parent(*wid.to_widget(ktouch.x, ktouch.y))
            ktouch.grab_current = wid
            ktouch.grab_state   = True
            wid.dispatch_event('on_touch_move', ktouch)
            ktouch.grab_state   = False
            ktouch.grab_current = None
            ktouch.pop()
        return ret


    def on_touch_up(self, touch):
        if touch.grab_current != self:
            return
        touch.ungrab(self)
        if id(touch) not in self.touch:
            return
        ktouch = self.touch[id(touch)]
        ktouch.userdata = touch.userdata
        ktouch.mode = 'spinning'

    def process_kinetic(self):
        '''Processing of kinetic, called in draw time.'''
        dt = getFrameDt()
        todelete = []

        for touchID in self.touch:
            ktouch = self.touch[touchID]

            if ktouch.mode != 'spinning':
                continue

            # process kinetic
            type        = ''
            ktouch.x    += ktouch.X
            ktouch.y    += ktouch.Y
            ktouch.X    /= 1 + (self.friction * dt)
            ktouch.Y    /= 1 + (self.friction * dt)

            if Vector(ktouch.X, ktouch.Y).length() < self.velstop:
                # simulation finished
                type = 'up'
                getAvailableTouchs().remove(ktouch)
                super(MTKinetic, self).on_touch_up(ktouch)
                todelete.append(touchID)
            else:
                # simulation in progress
                type = 'move'
                super(MTKinetic, self).on_touch_move(ktouch)

            # dispatch ktouch also in grab mode
            for wid in ktouch.grab_list:
                ktouch.push()
                ktouch.x, ktouch.y = self.to_window(*ktouch.pos)
                if wid.parent:
                    ktouch.x, ktouch.y = wid.parent.to_widget(ktouch.x, ktouch.y)
                else:
                    ktouch.x, ktouch.y = wid.to_parent(*wid.to_widget(ktouch.x, ktouch.y))
                ktouch.grab_current = wid
                ktouch.grab_state   = True
                if type == 'move':
                    wid.dispatch_event('on_touch_move', ktouch)
                else:
                    wid.dispatch_event('on_touch_up', ktouch)
                ktouch.grab_state   = False
                ktouch.grab_current = None
                ktouch.pop()

        # remove finished event
        for touchID in todelete:
            del self.touch[touchID]


    def draw(self):
        self.process_kinetic()

MTWidgetFactory.register('MTKinetic', MTKinetic)
