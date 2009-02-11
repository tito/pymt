import sys
import os

from math import *
from math import sqrt, sin
from pyglet import *
from pyglet.gl import *
from pyglet.text import HTMLLabel, Label
from pyglet.window import key
from pymt.graphx import *
from pymt.mtpyglet import *
from pymt.ui.animation import *
from pymt.ui.factory import *
from pymt.vector import Vector



_id_2_widget = {}

def getWidgetByID(id):
    global _id_2_widget
    if _id_2_widget.has_key(id):
        return _id_2_widget[id]

_event_stats = {}
_event_stats_activate = False

def event_stats_activate(activate=True):
    '''Activate or deactivate debug info on event'''
    global _event_stats_activate
    _event_stats_activate = activate

def event_stats_print():
    '''Print actual event stats'''
    print '[ Event stats ] ---------------------------------'
    global _event_stats
    for k in _event_stats:
        print '| %6d | %s' % (_event_stats[k], k)
    print '-------------------------------------------------'

class MTWidget(pyglet.event.EventDispatcher):
    '''Global base for any multitouch widget.
    Implement event for mouse, object, touch and animation.

    Event are dispatched through widget only if it's visible.

    :Parameters:
        `pos` : list, default is (0, 0)
            Position of widget, in (x, y) format
        `size` : list, default is (100, 100)
            Size of widget, in (width, height) format
        `size` : list, default is (.2, .2, .2, 1)
            Color of widget, in (r, v, b, a) format
        `visible` : bool, default is True
            Visibility of widget
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('pos', (0, 0))
        kwargs.setdefault('size', (100, 100))
        kwargs.setdefault('color', (.2, .2, .2, 1))
        kwargs.setdefault('visible', True)

        global _id_2_widget
        if kwargs.has_key('id'):
            self.id = kwargs.get('id')
            _id_2_widget[kwargs.get('id')] = self

        pyglet.event.EventDispatcher.__init__(self)
        self.parent					= None
        self.children				= []
        self._visible				= False
        self._x, self._y			= kwargs.get('pos')
        self._width, self._height	= kwargs.get('size')
        self._color					= kwargs.get('color')
        self.animations				= []
        self.visible				= kwargs.get('visible')

        self.register_event_type('on_resize')
        self.register_event_type('on_move')

        self.init()

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self.update_event_registration()
    def _get_visible(self):
        return self._visible
    visible = property(_get_visible, _set_visible)

    def _set_x(self, x):
        self._x = x
        self.dispatch_event('on_move', self.x, self.y)
    def _get_x(self):
        return self._x
    x = property(_get_x, _set_x)

    def _set_y(self, y):
        self._y = y
        self.dispatch_event('on_move', self.x, self.y)
    def _get_y(self):
        return self._y
    y = property(_get_y, _set_y)

    def _set_width(self, w):
        self._width = w
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_width(self):
        return self._width
    width = property(_get_width, _set_width)

    def _set_height(self, h):
        self._height = h
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_height(self):
        return self._height
    height = property(_get_height, _set_height)

    def _get_center(self):
        return (self._x + self._width/2, self._y+self._height/2)
    def _set_center(self, center):
        self._x = self.pos[0] - self.width/2
        self._y = self.pos[1] - self.height/2
        self.dispatch_event('on_move', self._x, self._y)
    center = property(_get_center, _set_center)

    def _set_pos(self, pos):
        self._x, self._y = pos
        self.dispatch_event('on_move', self._x, self._y)
    def _get_pos(self):
        return (self.x, self.y)
    pos = property(_get_pos, _set_pos)

    def _set_size(self, size):
        self.width, self.height = size
        self.dispatch_event('on_resize', self.width, self.height)
    def _get_size(self):
        return (self.width, self.height)
    size = property(_get_size, _set_size)

    def _get_color(self):
        return self._color
    def _set_color(self, col):
        if len(col) == 3:
            self._color = (col[0], col[1], col[2], 1.0)
        if len(col) == 4:
            self._color = col
    color = property(_get_color, _set_color)


    def dispatch_event(self, event_type, *args):
        '''Dispatch a single event to the attached handlers.

        The event is propogated to all handlers from from the top of the stack
        until one returns `EVENT_HANDLED`.  This method should be used only by
        `EventDispatcher` implementors; applications should call
        the ``dispatch_events`` method.

        :Parameters:
            `event_type` : str
                Name of the event.
            `args` : sequence
                Arguments to pass to the event handler.

        '''
        #assert event_type in self.event_types
        if event_type not in self.event_types: return

        # Search handler stack for matching event handlers
        for frame in self._event_stack:
            handler = frame.get(event_type, None)
            if handler:
                try:
                    if handler(*args):
                        return True
                except TypeError:
                    self._raise_dispatch_exception(event_type, args, handler)


        # Check instance for an event handler
        if hasattr(self, event_type):
            try:
                # Statistics
                global _event_stats_activate
                if _event_stats_activate:
                    global _event_stats
                    if not _event_stats.has_key(event_type):
                        _event_stats[event_type] = 1
                    else:
                        _event_stats[event_type] = _event_stats[event_type] + 1

                # Call event
                if getattr(self, event_type)(*args):
                    return True
            except TypeError:
                self._raise_dispatch_exception(
                    event_type, args, getattr(self, event_type))


    def update_event_registration(self):
        evs = [ 'on_draw',
                'on_mouse_press',
                'on_mouse_drag',
                'on_mouse_release',
                'on_touch_up',
                'on_touch_move',
                'on_touch_down',
                'on_object_up',
                'on_object_move',
                'on_object_down',
                'on_animation_complete',
                'on_animation_reset',
                'on_animation_start' ]

        if self.visible:
            for ev in evs:
                self.register_event_type(ev)
        else:
            for ev in evs:
                if not hasattr(self, 'event_types'):
                    continue
                if ev in self.event_types:
                    self.event_types.remove(ev)

    def to_local(self,x,y):
        lx = (x - self.x)
        ly = (y - self.y)
        return (lx,ly)

    def collide_point(self, x, y):
        if( x > self.x  and x < self.x + self.width and
           y > self.y and y < self.y + self.height  ):
            return True

    def init(self):
        pass


    def get_parent_window(self):
        return self.parent.get_parent_window()

    def bring_to_front(self):
        '''Remove it from wherever it is and add it back at the top'''
        if self.parent:
            self.parent.children.remove(self)
            self.parent.children.append(self)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def on_draw(self):
        if not self.visible:
            return

        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')

    def draw(self):
        pass

    def add_widget(self, w, front=True):
        if front:
            self.children.append(w)
        else:
            self.children.insert(0,w)
        try:
            w.parent = self
        except:
            pass

    def remove_widget(self, w):
        try:
            self.children.remove(w)
        except:
            pass

    def add_animation(self, label, prop, to , timestep, length,
                      func=AnimationAlpha.ramp):
        anim = Animation(self, label, prop, to, timestep, length, func=func)
        self.animations.append(anim)
        return anim

    def start_animations(self, label='all'):
        for anim in self.animations:
            if anim.label == label or label == 'all':
                anim.reset()
                anim.start()

    def remove_animation(self, label):
        for anim in self.animations:
            if anim.label == label:
                self.animations.remove(anim)

    def on_resize(self, w, h):
        for c in self.children:
            c.dispatch_event('on_resize', w, h)

    def on_move(self, x, y):
        for c in self.children:
            c.dispatch_event('on_move', x, y)

    def on_touch_down(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_down', touches, touchID, x, y):
                return True

    def on_touch_move(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_move', touches, touchID, x, y):
                return True

    def on_touch_up(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_up', touches, touchID, x, y):
                return True

    def on_mouse_press(self, x, y, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_press',x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_drag',x, y, dx, dy, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_object_down(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_down', touches, touchID,id, x, y,angle)

    def on_object_move(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_move', touches, touchID,id, x, y,angle)

    def on_object_up(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_up', touches, touchID,id, x, y,angle)


# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
