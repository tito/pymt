'''
Widget: Base of every widget implementation.
'''

__all__ = ['getWidgetById','getWidgetByID',
    'event_stats_activate', 'event_stats_print',
    'MTWidget'
]

import sys
import os
import weakref
from ...event import EventDispatcher
from ...logger import pymt_logger
from ...base import getCurrentTouches
from ...input import Touch
from ...utils import SafeList
from ..animation import Animation, AnimationAlpha
from ..factory import MTWidgetFactory
from ..colors import css_get_style
from ...graphx import set_color, drawCSSRectangle

_id_2_widget = {}

def getWidgetById(id):
    global _id_2_widget
    if id not in _id_2_widget:
        return
    ref = _id_2_widget[id]
    obj = ref()
    if not obj:
        del _id_2_widget[id]
        return
    return obj
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

    __slots__ = ('cls', 'children', 'style', 'draw_children',
                 '_root_window_source', '_root_window',
                 '_parent_window_source', '_parent_window',
                 '_size_hint', '_id', '_parent',
                 '_visible', '_inline_style',
                 '__weakref__')

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
        kwargs.setdefault('size_hint', (None, None))
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

        super(MTWidget, self).__init__(**kwargs)

        # Registers events
        for ev in MTWidget.visible_events:
            self.register_event_type(ev)

        self._parent              = None
        self.children             = SafeList()
        self._visible             = False
        self._size_hint           = kwargs.get('size_hint')
        self.visible              = kwargs.get('visible')
        self.draw_children        = kwargs.get('draw_children')

        # cache for get_parent_window()
        self._parent_window         = None
        self._parent_window_source  = None
        self._root_window           = None
        self._root_window_source    = None

        self.register_event_type('on_animation_complete')
        self.register_event_type('on_resize')
        self.register_event_type('on_parent_resize')
        self.register_event_type('on_move')
        self.register_event_type('on_parent')

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
        self._inline_style = kwargs.get('style')
        if len(kwargs.get('style')):
            self.apply_css(kwargs.get('style'))

        self.init()


    def _set_parent(self, parent):
        self._parent = parent
        self.dispatch_event('on_parent')
    def _get_parent(self):
        return self._parent
    parent = property(lambda self: self._get_parent(),
                      lambda self, x: self._set_parent(x),
                      doc='MTWidget: parent of widget. Fired on_parent event when set')

    def _set_id(self, id):
        global _id_2_widget
        ref = weakref.ref(self)
        if ref in _id_2_widget:
            del _id_2_widget[self._id]
        self._id = id
        if self._id:
            if ref in _id_2_widget:
                pymt_logger.warning('Widget: ID <%s> is already used ! Replacing with new one.' % id)
            _id_2_widget[self._id] = ref
    def _get_id(self):
        return self._id
    id = property(lambda self: self._get_id(),
                  lambda self, x: self._set_id(x),
                  doc='str: id of widget')

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
    def _get_visible(self):
        return self._visible
    visible = property(lambda self: self._get_visible(),
                       lambda self, x: self._set_visible(x),
                       doc='bool: visibility of widget')

    def _set_size_hint(self, size_hint):
        if self._size_hint == size_hint:
            return False
        self._size_hint = size_hint
    def _get_size_hint(self):
        return self._size_hint
    size_hint = property(lambda self: self._get_size_hint(),
                         lambda self, x: self._set_size_hint(x),
                         doc='size_hint is used by layouts to determine size behaviour during layout')

    def apply_css(self, styles):
        '''Called at __init__ time to applied css attribute in current class.
        '''
        self.style.update(styles)

    def reload_css(self, styles):
        '''Called when css want to be reloaded from scratch'''
        self.style = {}
        self.apply_css(styles)
        if len(self._inline_style):
            self.apply_css(self._inline_style)

    def to_widget(self, x, y):
        '''Return the coordinate from window to local widget'''
        if self.parent:
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
        if not self.visible:
            return False
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
        if not self.visible:
            return
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
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

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

    def on_parent(self):
        pass


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

    # generate event for all baseobject methods

    def _set_pos(self, x):
        if super(MTWidget, self)._set_pos(x):
            self.dispatch_event('on_move', *self._pos)
            return True

    def _set_x(self, x):
        if super(MTWidget, self)._set_x(x):
            self.dispatch_event('on_move', *self._pos)
            return True

    def _set_y(self, x):
        if super(MTWidget, self)._set_y(x):
            self.dispatch_event('on_move', *self._pos)
            return True

    def _set_size(self, x):
        if super(MTWidget, self)._set_size(x):
            self.dispatch_event('on_resize', *self._size)
            return True

    def _set_width(self, x):
        if super(MTWidget, self)._set_width(x):
            self.dispatch_event('on_resize', *self._size)
            return True

    def _set_height(self, x):
        if super(MTWidget, self)._set_height(x):
            self.dispatch_event('on_resize', *self._size)
            return True


# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
