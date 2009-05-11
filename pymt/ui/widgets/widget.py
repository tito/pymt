'''
Widget: Base of every widget implementation.
'''

__all__ = ['getWidgetById',
    'event_stats_activate', 'event_stats_print',
    'MTWidget'
]

import sys
import os
import pyglet
from ...logger import pymt_logger
from ..animation import Animation, AnimationAlpha
from ..factory import MTWidgetFactory
from ..colors import css_get_style


_id_2_widget = {}

def getWidgetById(id):
    global _id_2_widget
    if id in _id_2_widget:
        return _id_2_widget[id]
getWidgetByID = getWidgetById

_event_stats = {}
_event_stats_activate = False

def event_stats_activate(activate=True):
    '''Activate or deactivate debug info on event'''
    global _event_stats_activate
    _event_stats_activate = activate

def event_stats_print():
    '''Print actual event stats'''
    pymt_logger.info('Event stats')
    global _event_stats
    for k in _event_stats:
        pymt_logger.info('%6d: %s' % (_event_stats[k], k))

class MTWidget(pyglet.event.EventDispatcher):
    '''Global base for any multitouch widget.
    Implement event for mouse, object, touch and animation.

    Event are dispatched through widget only if it's visible.

    :Parameters:
        `pos` : list, default is (0, 0)
            Position of widget, in (x, y) format
        `x` : int, default is None
            X position of widget
        `y` : int, default is None
            Y position of widget
        `size` : list, default is (100, 100)
            Size of widget, in (width, height) format
        `width` : int, default is None
            width position of widget
        `height` : int, default is None
            height position of widget
        `visible` : bool, default is True
            Visibility of widget
        `draw_children` : bool, default is True
            Indicate if children will be draw, or not
        `no_css` : bool, default is False
            Don't search/do css for this widget
        `inner_animation` : custom, default is ()
            You can activate default inner animation with this keyword
            Format is: ('pos', ('size': {func=AnimationAlpha.sin}), )

    :Events:
        `on_draw` ()
            Used to draw the widget and his children.
        `on_mouse_press` (int x, int y, int button, int modifiers)
            Fired when mouse is pressed
        `on_mouse_release` (int x, int y, int button, int modifiers)
            Fired when mouse is release
        `on_mouse_drag` (int x, int y, int dx, int dy, int button, int modifiers)
            Fired when mouse is draw
        `on_touch_down` (list:Tuio2dCursor touches, int touchID, int x, int y)
            Fired when a blob appear
        `on_touch_move` (list:Tuio2dCursor touches, int touchID, int x, int y)
            Fired when a blob is moving
        `on_touch_up` (list:Tuio2dCursor touches, int touchID, int x, int y)
            Fired when a blob disappear
        `on_object_down` (list:Tuio2dObject objects, int objectID, int x, int y, float angle)
            Fired when an object appear
        `on_object_move` (list:Tuio2dObject objects, int objectID, int x, int y, float angle)
            Fired when an object is moving
        `on_object_up` (list:Tuio2dObject objects, int objectID, int x, int y, float angle)
            Fired when an object disappear
    '''
    visible_events = [
        'on_draw',
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
        'on_animation_start'
    ]
    def __init__(self, **kwargs):
        kwargs.setdefault('pos', (0, 0))
        kwargs.setdefault('x', None)
        kwargs.setdefault('y', None)
        kwargs.setdefault('size', (100, 100))
        kwargs.setdefault('width', None)
        kwargs.setdefault('height', None)
        kwargs.setdefault('visible', True)
        kwargs.setdefault('draw_children', True)
        kwargs.setdefault('no_css', False)
        kwargs.setdefault('inner_animation', ())

        self._id = None
        if 'id' in kwargs:
            self.id = kwargs.get('id')

        pyglet.event.EventDispatcher.__init__(self)

        # Registers events
        for ev in MTWidget.visible_events:
            self.register_event_type(ev)

        self.parent					= None
        self.children				= []
        self._visible				= False
        self._x, self._y			= kwargs.get('pos')
        self._width, self._height	= kwargs.get('size')
        self.animations				= []
        self.visible				= kwargs.get('visible')
        self.draw_children          = kwargs.get('draw_children')

        self.register_event_type('on_resize')
        self.register_event_type('on_move')

        if kwargs.get('x'):
            self.x = kwargs.get('x')
        if kwargs.get('y'):
            self.y = kwargs.get('y')
        if kwargs.get('width'):
            self.width = kwargs.get('width')
        if kwargs.get('height'):
            self.height = kwargs.get('height')

        # apply css
        if not kwargs.get('no_css'):
            style = css_get_style(widget=self)
            self.apply_css(style)

        self.a_properties = {}
        for prop in kwargs.get('inner_animation'):
            kw = dict()
            if type(prop) in (list, tuple):
                prop, kw = prop
            self.enable_inner_animation(prop, **kw)

        self.init()

    def _set_id(self, id):
        global _id_2_widget
        if self._id and self._id in _id_2_widget:
            del _id_2_widget[self._id]
        self._id = id
        if self._id:
            _id_2_widget[self._id] = self
    def _get_id(self):
        return self._id
    id = property(_get_id, _set_id, doc='str: id of widget')

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
    def _get_visible(self):
        return self._visible
    visible = property(_get_visible, _set_visible, doc='bool: visibility of widget')

    def _set_x(self, x):
        if self._x == x:
            return
        self._x = x
        self.dispatch_event('on_move', self.x, self.y)
    def _get_x(self):
        return self._x
    x = property(_get_x, _set_x, doc='int: X position of widget')

    def _set_y(self, y):
        if self._y == y:
            return
        self._y = y
        self.dispatch_event('on_move', self.x, self.y)
    def _get_y(self):
        return self._y
    y = property(_get_y, _set_y, doc='int: Y position of widget')

    def _set_width(self, w):
        if self._width == w:
            return
        self._width = w
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_width(self):
        return self._width
    width = property(_get_width, _set_width, doc='int: width of widget')

    def _set_height(self, h):
        if self._height == h:
            return
        self._height = h
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_height(self):
        return self._height
    height = property(_get_height, _set_height, doc='int: height of widget')

    def _get_center(self):
        return (self._x + self._width/2, self._y+self._height/2)
    def _set_center(self, center):
        self.pos = (center[0] - self.width/2, center[1] - self.height/2)
    center = property(_get_center, _set_center, doc='tuple(x, y): center of widget')

    def _set_pos(self, pos):
        if self._x == pos[0] and self._y == pos[1]:
            return
        self._x, self._y = pos
        self.dispatch_event('on_move', self._x, self._y)
    def _get_pos(self):
        return (self._x, self._y)
    pos = property(_get_pos, _set_pos, doc='tuple(x, y): position of widget')

    def _set_size(self, size):
        if self._width == size[0] and self._height == size[1]:
            return
        self._width, self._height = size
        self.dispatch_event('on_resize', self.width, self.height)
    def _get_size(self):
        return (self.width, self.height)
    size = property(_get_size, _set_size,
                    doc='tuple(width, height): width/height of widget')

    def apply_css(self, styles):
        '''Called at __init__ time to applied css attribute in current class.
        '''
        pass

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

        # Don't dispatch event for visible widget if we are not visible
        if event_type in MTWidget.visible_events and not self.visible:
            return

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
                    if not event_type in _event_stats:
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
        if self.visible:
            for ev in evs:
                self.register_event_type(ev)
        else:
            for ev in evs:
                if not hasattr(self, 'event_types'):
                    continue
                if ev in self.event_types:
                    self.event_types.remove(ev)

    def to_local(self, x, y):
        '''Return the (x,y) coordinate in the local plan of widget'''
        lx = (x - self.x)
        ly = (y - self.y)
        return (lx, ly)

    def collide_point(self, x, y):
        '''Test if the (x,y) is in widget bounding box'''
        if( x > self.x  and x < self.x + self.width and
           y > self.y and y < self.y + self.height  ):
            return True

    def init(self):
        pass

    def get_parent_window(self):
        '''Return the parent window of widget'''
        if self.parent:
            return self.parent.get_parent_window()
        return None

    def get_parent_layout(self):
        '''Return the parent layout of widget'''
        if self.parent:
            return self.parent.get_parent_layout()
        return None

    def bring_to_front(self):
        '''Remove it from wherever it is and add it back at the top'''
        if self.parent:
            self.parent.children.remove(self)
            self.parent.children.append(self)

    def hide(self):
        '''Hide the widget'''
        self.visible = False

    def show(self):
        '''Show the widget'''
        self.visible = True

    def on_draw(self):
        if not self.visible:
            return

        self.draw()
        if self.draw_children:
            for w in self.children:
                w.dispatch_event('on_draw')

    def draw(self):
        '''Handle the draw of widget.
        Derivate this method to draw your widget.'''
        pass

    def add_widget(self, w, front=True):
        '''Add a widget in the children list.'''
        if front:
            self.children.append(w)
        else:
            self.children.insert(0,w)
        try:
            w.parent = self
        except:
            pass

    def remove_widget(self, w):
        '''Remove a widget from the children list'''
        if w in self.children:
            self.children.remove(w)

    def add_animation(self, *largs, **kwargs):
        '''Add an animation in widget.'''
        anim = Animation(self, *largs, **kwargs)
        self.animations.append(anim)
        return anim

    def start_animations(self, label='all'):
        '''Start all widget animation that match the label'''
        for anim in self.animations:
            if anim.label == label or label == 'all':
                anim.reset()
                anim.start()

    def stop_animations(self, label='all'):
        '''Stop all widget animation that match the label'''
        for anim in self.animations:
            if anim.label == label or label == 'all':
                anim.stop()

    def remove_animation(self, label):
        '''Remove widget animation that match the label'''
        for anim in self.animations:
            if anim.label == label:
                self.animations.remove(anim)

    def enable_inner_animation(self, props, **kwargs):
        '''Activate inner animation for listed properties'''
        if type(props) == tuple:
            props = list(props)
        elif type(props) == str:
            props = [props, ]
        accepted_kw = ['timestep', 'length', 'func']
        for k in kwargs:
            if k not in accepted_kw:
                raise Exception('Invalid keyword %s' % k)
        for prop in props:
            self.a_properties[prop] = kwargs

    def disable_inner_animation(self, props):
        '''Deactivate inner animation for listed properties'''
        props = list(props)
        for prop in props:
            if prop in self.a_properties:
                del self.a_properties[prop]

    def update_inner_animation(self):
        if not hasattr(self, 'a_properties'):
            return
        if len(self.a_properties):
            self.__setattr__ = self.__setattr_inner_animation__
        else:
            self.__setattr__ = super(MTWidget, self).__setattr__

    def __setattr__(self, name, value, inner=False):
        if hasattr(self, 'a_properties') and len(self.a_properties) \
            and name in self.a_properties and not inner:
            label = '__%s' % name
            kw = self.a_properties[name]
            kw.setdefault('timestep', 1./60)
            kw.setdefault('length', 1.)
            kw['inner'] = True
            kw['prop']  = name
            kw['to']    = value

            # remove old animation
            self.stop_animations(label=label)
            self.remove_animation(label=label)

            # add new
            self.add_animation(label=label, **kw)
            self.start_animations(label=label)
        else:
            super(MTWidget, self).__setattr__(name, value)

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
            if w.dispatch_event('on_mouse_press',x, y, button, modifiers):
                return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for w in reversed(self.children):
            if w.dispatch_event('on_mouse_drag',x, y, dx, dy, button, modifiers):
                return True

    def on_mouse_release(self, x, y, button, modifiers):
        for w in reversed(self.children):
            if w.dispatch_event('on_mouse_release', x, y, button, modifiers):
                return True

    def on_object_down(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            if w.dispatch_event('on_object_down', touches, touchID,id, x, y, angle):
                return True

    def on_object_move(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            if w.dispatch_event('on_object_move', touches, touchID,id, x, y, angle):
                return True

    def on_object_up(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            if w.dispatch_event('on_object_up', touches, touchID,id, x, y,angle):
                return True


# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
