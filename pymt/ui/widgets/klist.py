'''
List: a list with kinetic effect
'''

__all__ = ('MTList', 'MTListContainer')

from pymt.graphx import gx_matrix
from pymt.utils import boundary
from pymt.base import getFrameDt
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.widgets.stencilcontainer import MTStencilContainer
from pymt.config import pymt_config
from OpenGL.GL import glTranslatef

#
# Split between List and ListContainer is done
# because we don't want to duplicate on_draw from
# StencilWidget
#

class MTListContainer(MTWidget):
    '''Container for MTList.

    .. warning::
        The size of this container is taken from the first children size.

    '''
    def __init__(self, **kwargs):
        super(MTListContainer, self).__init__(**kwargs)
        self.content_x = 0
        self.content_y = 0

    def on_update(self):
        super(MTListContainer, self).on_update()
        if self.children:
            self.size = self.children[0].size

    def on_draw(self):
        with gx_matrix:
            glTranslatef(self.x + self.content_x, self.y + self.content_y, 0)
            for children in self.children[:]:
                children.dispatch_event('on_draw')

class MTList(MTStencilContainer):
    '''List with kinetic. This is the replacement of old MTKineticList().
    The MTList widget are able to scroll in 2 way, and use your widgets.

    .. warning::
        The MTList have the same behavior as MTScatterWidget: coordinates of his
        children are relative to the MTList (not fixed to the screen.)


    The MTList use a Stencil container, to prevent drawing outside his size.
    Then, it use a MTListContainer to be able to scroll his content. The
    MTListContainer size is taken from the first children in the list. We
    recommend you to use a layout for the list. Check the examples at the end of
    the page about how to use your widgets inside a layout, in the MTList.

    Some parameters are customizable in global configuration ::

        [widgets]
        list_friction = 10
        list_trigger_distance = 5

    :Parameters:
        `do_x`: bool, default to True
            Allow scrolling on X axis
        `do_y`: bool, default to True
            Allow scrolling on Y axis
        `friction`: int, default to 10 (list_friction in conf)
            Friction of scrolling movement. The formula is ::

                acceleration = 1 + friction * frame_delta_time

        `friction_bound`: int, default to 10 (list_friction_bound in conf)
            Friction of scrolling movement when position are outside bounds.
        `trigger_distance`: int, default to 5 (list_trigger_distance in config)
            If the distance between the position of the first touch contact to
            the second position is less than the trigger_distance, a event
            'down' and 'up' are dispatched on the childrens.
            Otherwise, no event are dispatched.
            (If you move the list to much, no event will be dispatched.)
        `max_acceleration`: int, default to 50
            Maximum acceleration allowed when movement is calculated
    '''
    def __init__(self, **kwargs):
        super(MTList, self).__init__(**kwargs)
        self.do_x = kwargs.get('do_x', True)
        self.do_y = kwargs.get('do_y', True)
        self.trigger_distance = kwargs.get('trigger_distance',
            pymt_config.getint('widgets', 'list_trigger_distance'))
        self.friction = kwargs.get('friction',
            pymt_config.getint('widgets', 'list_friction'))
        self.friction_bound = kwargs.get('friction',
            pymt_config.getint('widgets', 'list_friction_bound'))
        self.max_acceleration = kwargs.get('max_acceleration', 50)
        self._is_controled = False
        self.content_x = 0
        self.content_y = 0
        self._vx = 0
        self._vy = 0
        self.container = MTListContainer()
        super(MTList, self).add_widget(self.container)

    def add_widget(self, *largs):
        self.container.add_widget(*largs)

    def remove_widget(self, *largs):
        self.container.remove_widget(*largs)

    def process_kinetic(self):
        dt = getFrameDt()
        friction = self.friction
        container = self.container
        cw = container.width - self.width
        ch = container.height - self.height
        cx = self.content_x
        cy = self.content_y
        vx = self._vx
        vy = self._vy

        # prevent too much calculation at idle state
        if abs(vx) < 0.01:
            vx = 0
        if abs(vy) < 0.01:
            vy = 0

        # apply friction for movement
        if vx or vy:
            vx /= 1 + (friction * dt)
            vy /= 1 + (friction * dt)
            if self._is_controled is False:
                cx -= vx * self.do_x
                cy -= vy * self.do_y

        if self._is_controled is False:
            # make the content back to origin if it's out of bounds
            # don't go back to the initial bound, but use friction to do it in a
            # smooth way.
            #
            # if the container is smaller than our width, always align to left
            # XXX should be customizable.
            #
            f = 1 + self.friction_bound * dt
            smaller = self.width > container.width
            if cx > 0 or smaller:
                cx /= f
                vx = 0
            elif cx < -cw and not smaller:
                a = (cw + cx) / f
                cx = -cw + a
                vx = 0
            smaller = self.height > container.height
            if cy > 0 or smaller:
                cy /= f
                vy = 0
            elif cy < -ch and not smaller:
                a = (ch + cy) / f
                cy = -ch + a
                vy = 0

        # update our values
        self.content_x = container.content_x = cx
        self.content_y = container.content_y = cy
        container.pos = self.pos
        self._vx = vx
        self._vy = vy

    def on_touch_down(self, touch):
        ret = self.collide_point(*touch.pos)
        if self._is_controled:
            return ret
        if ret:
            touch.userdata['list.startpos'] = self.content_x, self.content_y
            touch.grab(self)
            self._is_controled = True
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        cx, cy = touch.userdata['list.startpos']
        acceleration = self.max_acceleration
        if self.do_x:
            self.content_x = touch.x - touch.oxpos + cx
            self._vx += touch.dxpos - touch.x
            self._vx = boundary(self._vx, -acceleration, acceleration)
        if self.do_y:
            self.content_y = touch.y - touch.oypos + cy
            self._vy += touch.dypos - touch.y
            self._vy = boundary(self._vy, -acceleration, acceleration)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        self._is_controled = False

        # check if we can transmit event to children
        trigger_distance = self.trigger_distance
        if (self.do_x and abs(touch.oxpos - touch.x) > trigger_distance) or \
           (self.do_y and abs(touch.oypos - touch.y) > trigger_distance):
            return True

        # ok, the trigger distance is enough, we can dispatch event.
        # will not work if children grab the touch in down state :/
        grab_current = touch.grab_current
        grab_list = touch.grab_list[:]
        touch.push()
        touch.x -= self.content_x + self.x
        touch.y -= self.content_y + self.y

        # difficult part.
        # first, we should dispatch event as base should do
        # then, in second, we must dispatch event for widgets in the grab list
        touch.grab_current = None
        for child in reversed(self.container.children[:]):
            if child.dispatch_event('on_touch_down', touch):
                break
        for child in reversed(self.container.children[:]):
            if child.dispatch_event('on_touch_up', touch):
                break

        # now, dispatch with grab_current
        # only for new grab
        for ref in [x for x in touch.grab_list if x not in grab_list]:
            # grab are weakref, check them
            child = ref()
            if child is None:
                continue
            touch.grab_current = child
            child.dispatch_event('on_touch_up', touch)

        touch.pop()
        touch.grab_current = grab_current

        return True

    def on_update(self):
        super(MTList, self).on_update()
        self.process_kinetic()

    def on_draw(self):
        super(MTList, self).draw()
        super(MTList, self).on_draw()

    def draw(self):
        pass
