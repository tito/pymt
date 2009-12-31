'''
Widget: Base of every widget implementation.
'''

__all__ = ['getWidgetById',
    'event_stats_activate', 'event_stats_print',
    'MTWidget'
]

import sys
import os
from ...event import EventDispatcher
from ...logger import pymt_logger
from ...base import getCurrentTouches
from ...input import Touch
from ...utils import SafeList
from ..animation import Animation, AnimationAlpha
from ..factory import MTWidgetFactory
from ..colors import css_get_style

import inspect


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
    pymt_logger.info('Widget: Event stats')
    global _event_stats
    for k in _event_stats:
        pymt_logger.info('Widget: %6d: %s' % (_event_stats[k], k))

class MTWidget(EventDispatcher):
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
            Don't search/do CSS for this widget
		`style` : dict, default to {}
			Add inline CSS
		`cls` : str, default is ''
			CSS class of this widget

    :Events:
        `on_update` ()
            Used to update the widget and his children.
        `on_draw` ()
            Used to draw the widget and his children.
        `on_touch_down` (Touch touch)
            Fired when a blob appear
        `on_touch_move` (Touch touch)
            Fired when a blob is moving
        `on_touch_up` (Touch touch)
            Fired when a blob disappear
        `on_resize` (float width, float height)
            Fired when widget is resized
        `on_parent_resize` (float width, float height)
            Fired when parent widget is resized
    '''
    visible_events = [
        'on_update',
        'on_draw',
        'on_touch_up',
        'on_touch_move',
        'on_touch_down'
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
        kwargs.setdefault('cls', '')
        kwargs.setdefault('style', {})

        self._id = None
        if 'id' in kwargs:
            self.id = kwargs.get('id')

        super(MTWidget, self).__init__()

        # Registers events
        for ev in MTWidget.visible_events:
            self.register_event_type(ev)

        self.parent					= None
        self.children				= SafeList()
        self._visible				= False
        self._x, self._y			= kwargs.get('pos')
        self._width, self._height	= kwargs.get('size')
        self.animations				= []
        self.visible				= kwargs.get('visible')
        self.draw_children          = kwargs.get('draw_children')

        # cache for get_parent_window()
        self._parent_window         = None
        self._parent_window_source  = None
        self._parent_layout         = None
        self._parent_layout_source  = None
        self._root_window           = None
        self._root_window_source    = None

        self.register_event_type('on_animation_complete')
        self.register_event_type('on_resize')
        self.register_event_type('on_parent_resize')
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
        self.style = {}
        self.cls = kwargs.get('cls')
        if not kwargs.get('no_css'):
            style = css_get_style(widget=self)
            self.apply_css(style)

        # apply inline css
        if len(kwargs.get('style')):
            self.apply_css(kwargs.get('style'))

        self.a_properties = {}

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
        self.style.update(styles)

    def connect(self, p1, w2, p2=None, func=lambda x: x):
        '''Connect events to a widget property'''
        def lambda_connect(*largs):
            if type(p2) in (tuple, list):
                if len(largs) != len(p2):
                    pymt_logger.exception('Widget: cannot connect with different size')
                    raise
                for p in p2:
                    if p is None:
                        continue
                    w2.__setattr__(p, type(w2.__getattribute__(p))(
                        func(largs[p2.index(p)])))
            else:
                dtype = type(w2.__getattribute__(p2))
                try:
                    if len(largs) == 1:
                        w2.__setattr__(p2, dtype(func(*largs)))
                    else:
                        w2.__setattr__(p2, dtype(func(largs)))
                except Exception, e:
                    pymt_logger.exception('Widget: cannot connect with different size')
                    raise
        if p2 is None:
            self.push_handlers(**{p1: w2})
        else:
            self.push_handlers(**{p1: lambda_connect})

    def to_widget(self, x, y):
        '''Return the coordinate from window to local widget'''
        x, y = self.parent.to_widget(x, y)
        return self.to_local(x, y)

    def to_window(self, x, y, initial=True):
        '''Transform local coordinate to window coordinate'''
        if not initial:
            x, y = self.to_parent(x, y)
        if self.parent:
            return self.parent.to_window(x, y, initial=False)
        return (x, y)

    def to_parent(self, x, y):
        '''Transform local coordinate to parent coordinate'''
        return (x, y)

    def to_local(self, x, y):
        '''Transform parent coordinate to local coordinate'''
        return (x, y)

    def collide_point(self, x, y):
        '''Test if the (x,y) is in widget bounding box'''
        if( x > self.x  and x < self.x + self.width and
           y > self.y and y < self.y + self.height  ):
            return True

    def init(self):
        pass

    def get_root_window(self):
        '''Return the root window of widget'''
        if not self.parent:
            return None

        # cache value
        if self._root_window_source != self.parent or self._root_window is None:
            self._root_window = self.parent.get_root_window()
            if not self._root_window:
                return None
            self._root_window_source = self.parent

        return self._root_window

    def get_parent_window(self):
        '''Return the parent window of widget'''
        if not self.parent:
            return None

        # cache value
        if self._parent_window_source != self.parent or self._parent_window is None:
            self._parent_window = self.parent.get_parent_window()
            if not self._parent_window:
                return None
            self._parent_window_source = self.parent

        return self._parent_window

    def get_parent_layout(self):
        '''Return the parent layout of widget'''
        if not self.parent:
            return None

        # cache value
        if self._parent_layout_source != self.parent or self._parent_layout is None:
            self._parent_layout = self.parent.get_parent_layout()
            if not self._parent_layout:
                return None
            self._parent_layout_source = self.parent

        return self._parent_layout

    def bring_to_front(self):
        '''Remove it from wherever it is and add it back at the top'''
        if self.parent:
            parent = self.parent
            parent.remove_widget(self)
            parent.add_widget(self)

    def hide(self):
        '''Hide the widget'''
        self.visible = False

        # unregister all event used for drawing / interaction
        for ev in MTWidget.visible_events:
            self.unregister_event_type(ev)

    def show(self):
        '''Show the widget'''
        self.visible = True

        # register all event used for drawing / interaction
        for ev in MTWidget.visible_events:
            self.register_event_type(ev)

    def on_update(self):
        for w in self.children.iterate():
            w.dispatch_event('on_update')

    def on_draw(self):
        if not self.visible:
            return

        self.draw()
        if self.draw_children:
            for w in self.children.iterate():
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

    def add_widgets(self, *widgets):
        for w in widgets:
            self.add_widget(w)


    def remove_widget(self, w):
        '''Remove a widget from the children list'''
        if w in self.children:
            self.children.remove(w)

    def __setattr__(self, name, value):
        super(MTWidget, self).__setattr__(name, value)

    def on_parent_resize(self, w, h):
        pass

    def on_resize(self, w, h):
        for c in self.children.iterate():
            c.dispatch_event('on_parent_resize', w, h)

    def on_move(self, x, y):
        for c in self.children.iterate():
            c.dispatch_event('on_move', x, y)

    def on_touch_down(self, touch):
        for w in self.children.iterate(reverse=True):
            if w.dispatch_event('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        for w in self.children.iterate(reverse=True):
            if w.dispatch_event('on_touch_move', touch):
                return True

    def on_touch_up(self, touch):
        for w in self.children.iterate(reverse=True):
            if w.dispatch_event('on_touch_up', touch):
                return True

    def do(self,*largs):
        '''Apply/Start animations on the widgets.
        :Parameters:
            `animation` : Animation Object
                Animation object with properties to be animateds ","
        '''
        for arg in largs:
            if arg.set_widget(self):
                return arg.start(self)

# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
