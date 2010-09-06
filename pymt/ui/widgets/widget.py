'''
Widget: Base of every widget implementation.
'''

__all__ = ('getWidgetById', 'MTWidget')

import weakref
from pymt.event import EventDispatcher
from pymt.logger import pymt_logger
from pymt.utils import SafeList
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.colors import css_get_style
from pymt.graphx import set_color, drawCSSRectangle

_id_2_widget = dict()

def getWidgetById(widget_id):
    '''Get a widget by ID'''
    if widget_id not in _id_2_widget:
        return
    ref = _id_2_widget[widget_id]
    obj = ref()
    if not obj:
        del _id_2_widget[widget_id]
        return
    return obj


class MTWidgetMetaclass(type):
    '''Metaclass to auto register new widget into :ref:`MTWidgetFactory`
    .. warning::
        This metaclass is used for MTWidget. Don't use it directly !
    '''
    def __init__(mcs, name, bases, attrs):
        super(MTWidgetMetaclass, mcs).__init__(name, bases, attrs)
        # auto registration in factory
        MTWidgetFactory.register(name, mcs)

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

    __metaclass__ = MTWidgetMetaclass

    __slots__ = ('children', 'style', 'draw_children',
                 '_cls',
                 '_root_window_source', '_root_window',
                 '_parent_window_source', '_parent_window',
                 '_parent_layout_source', '_parent_layout',
                 '_size_hint', '_id', '_parent',
                 '_visible', '_inline_style',
                 '__animationcache__',
                 '__weakref__')

    visible_events = [
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
        kwargs.setdefault('cls', '')
        kwargs.setdefault('style', {})

        self._id = None
        if 'id' in kwargs:
            self.id = kwargs.get('id')

        super(MTWidget, self).__init__(**kwargs)

        # Registers events
        for ev in MTWidget.visible_events:
            self.register_event_type(ev)

        # privates
        self.__animationcache__   = set()
        self._parent              = None
        self._visible             = None
        self._size_hint           = kwargs.get('size_hint')


        #: List of children (SafeList)
        self.children             = SafeList()
        #: If False, childrens are not drawed. (deprecated)
        self.draw_children        = kwargs.get('draw_children')
        #: Dictionnary that contains the widget style
        self.style = {}

        # apply visibility
        self.visible              = kwargs.get('visible')

        # cache for get_parent_window()
        self._parent_layout         = None
        self._parent_layout_source  = None
        self._parent_window         = None
        self._parent_window_source  = None
        self._root_window           = None
        self._root_window_source    = None

        # register events
        register_event_type = self.register_event_type
        for event in ('on_update', 'on_animation_complete', 'on_resize',
                      'on_parent_resize', 'on_move', 'on_parent'):
            register_event_type(event)

        if kwargs.get('x'):
            self._pos = (kwargs.get('x'), self.y)
        if kwargs.get('y'):
            self._pos = (self.x, kwargs.get('y'))
        if kwargs.get('width'):
            self._size = (kwargs.get('width'), self.height)
        if kwargs.get('height'):
            self._size = (self.width, kwargs.get('height'))

        # apply style
        self._cls = ''
        self._inline_style = kwargs['style']

        # loading is done here automaticly
        self.cls = kwargs.get('cls')

    def _set_cls(self, cls):
        self._cls = cls
        self.reload_css()
    def _get_cls(self):
        return self._cls
    cls = property(_get_cls, _set_cls,
        doc='Get/Set the class of the widget (used for CSS, can be a string '
            'or a list of string')

    def _set_parent(self, parent):
        self._parent = parent
        self.dispatch_event('on_parent')
    def _get_parent(self):
        return self._parent
    parent = property(_get_parent, _set_parent,
                      doc='MTWidget: parent of widget. Fired on_parent event when set')

    def _set_id(self, id):
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
    id = property(_get_id, _set_id,
                  doc='str: id of widget')

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        # register or unregister event if the widget is visible or not
        if visible:
            for ev in MTWidget.visible_events:
                self.register_event_type(ev)
        else:
            for ev in MTWidget.visible_events:
                self.unregister_event_type(ev)
    def _get_visible(self):
        return self._visible
    visible = property(_get_visible, _set_visible, doc=''
        'True if the widget is visible. If False, the events on_draw,'
        'on_touch_down, on_touch_move, on_touch_up are not dispatched.')

    def _set_size_hint(self, size_hint):
        if self._size_hint == size_hint:
            return False
        self._size_hint = size_hint
    def _get_size_hint(self):
        return self._size_hint
    size_hint = property(_get_size_hint, _set_size_hint,
                         doc='size_hint is used by layouts to determine size behaviour during layout')

    def apply_css(self, styles):
        '''Called at __init__ time to applied css attribute in current class.
        '''
        self.style.update(styles)

    def reload_css(self):
        '''Called when css want to be reloaded from scratch'''
        self.style = {}
        style = css_get_style(widget=self)
        self.apply_css(style)
        if len(self._inline_style):
            self.apply_css(self._inline_style)

    def to_widget(self, x, y, relative=False):
        '''Return the coordinate from window to local widget'''
        if self.parent:
            x, y = self.parent.to_widget(x, y)
        return self.to_local(x, y, relative=relative)

    def to_window(self, x, y, initial=True, relative=False):
        '''Transform local coordinate to window coordinate'''
        if not initial:
            x, y = self.to_parent(x, y, relative=relative)
        if self.parent:
            return self.parent.to_window(x, y, initial=False, relative=relative)
        return (x, y)

    def to_parent(self, x, y, relative=False):
        '''Transform local coordinate to parent coordinate

        :Parameters:
            `relative`: bool, default to False
                Change to True is you want to translate relative position from
                widget to his parent.
        '''
        if relative:
            return (x + self.x, y + self.y)
        return (x, y)

    def to_local(self, x, y, relative=False):
        '''Transform parent coordinate to local coordinate

        :Parameters:
            `relative`: bool, default to False
                Change to True is you want to translate a coordinate to a
                relative coordinate from widget.
        '''
        if relative:
            return (x - self.x, y - self.y)
        return (x, y)

    def collide_point(self, x, y):
        '''Test if the (x,y) is in widget bounding box'''
        if not self.visible:
            return False
        if x > self.x  and x < self.x + self.width and \
           y > self.y and y < self.y + self.height:
            return True

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

    def show(self):
        '''Show the widget'''
        self.visible = True

    def on_update(self):
        for w in self.children[:]:
            w.dispatch_event('on_update')

    def on_draw(self):
        self.draw()
        if self.draw_children:
            for w in self.children[:]:
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
            self.children.insert(0, w)
        try:
            w.parent = self
        except Exception:
            pass

    def add_widgets(self, *widgets):
        for w in widgets:
            self.add_widget(w)


    def remove_widget(self, w):
        '''Remove a widget from the children list'''
        if w in self.children:
            self.children.remove(w)

    def on_animation_complete(self, *largs):
        pass

    def on_parent(self):
        pass

    def on_parent_resize(self, w, h):
        pass

    def on_resize(self, w, h):
        for c in self.children[:]:
            c.dispatch_event('on_parent_resize', w, h)

    def on_move(self, x, y):
        for c in self.children[:]:
            c.dispatch_event('on_move', x, y)

    def on_touch_down(self, touch):
        for w in reversed(self.children[:]):
            if w.dispatch_event('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        for w in reversed(self.children[:]):
            if w.dispatch_event('on_touch_move', touch):
                return True

    def on_touch_up(self, touch):
        for w in reversed(self.children[:]):
            if w.dispatch_event('on_touch_up', touch):
                return True

    def do(self, animation):
        '''Apply/Start animations on the widgets.

        :Parameters:
            `animation` : Animation Object
                Animation object with properties to be animateds ","
        '''
        if not animation.set_widget(self):
            return
        # XXX bug from Animation framework
        # we need to store a reference of our animation class
        # otherwise, if the animation is called with self.do(),
        # gc can suppress reference, and it's gone !
        animobj = animation.start(self)
        self.__animationcache__.add(animobj)
        def animobject_on_complete(widget, *l):
            if widget != self:
                return
            if animobj in self.__animationcache__:
                self.__animationcache__.remove(animobj)
        animation.connect('on_complete', animobject_on_complete)
        return animobj

    # generate event for all baseobject methods

    def _set_pos(self, x):
        if super(MTWidget, self)._set_pos(x):
            self.dispatch_event('on_move', *self._pos)
            return True
    pos = property(EventDispatcher._get_pos, _set_pos)

    def _set_x(self, x):
        if super(MTWidget, self)._set_x(x):
            self.dispatch_event('on_move', *self._pos)
            return True
    x = property(EventDispatcher._get_x, _set_x)

    def _set_y(self, x):
        if super(MTWidget, self)._set_y(x):
            self.dispatch_event('on_move', *self._pos)
            return True
    y = property(EventDispatcher._get_y, _set_y)

    def _set_size(self, x):
        if super(MTWidget, self)._set_size(x):
            self.dispatch_event('on_resize', *self._size)
            return True
    size = property(EventDispatcher._get_size, _set_size)

    def _set_width(self, x):
        if super(MTWidget, self)._set_width(x):
            self.dispatch_event('on_resize', *self._size)
            return True
    width = property(EventDispatcher._get_width, _set_width)

    def _set_height(self, x):
        if super(MTWidget, self)._set_height(x):
            self.dispatch_event('on_resize', *self._size)
            return True
    height = property(EventDispatcher._get_height, _set_height)

# install acceleration
try:
    import types
    from pymt.accelerate import accelerate
    if accelerate is not None:
        MTWidget.on_update = types.MethodType(accelerate.widget_on_update, None, MTWidget)
        MTWidget.on_draw = types.MethodType(accelerate.widget_on_draw, None, MTWidget)
        MTWidget.collide_point = types.MethodType(accelerate.widget_collide_point, None, MTWidget)
except ImportError, e:
    pymt_logger.warning('Widget: Unable to use accelerate module <%s>' % e)
