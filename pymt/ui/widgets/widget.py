'''
Widget: Base of every widget implementation.
'''

__all__ = ['getWidgetById',
    'event_stats_activate', 'event_stats_print',
    'MTWidget'
]

import sys
import os
import pymtcore
from ...logger import pymt_logger
from ...base import getAvailableTouchs
from ...input import Touch
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

class MTWidget(pymtcore.CoreWidget):
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
        `on_touch_down` (Touch touch)
            Fired when a blob appear
        `on_touch_move` (Touch touch)
            Fired when a blob is moving
        `on_touch_up` (Touch touch)
            Fired when a blob disappear
    '''
    visible_events = [
        'on_update',
        'on_draw',
        'on_mouse_press',
        'on_mouse_drag',
        'on_mouse_release',
        'on_touch_up',
        'on_touch_move',
        'on_touch_down',
        'on_animation_complete',
        'on_animation_reset',
        'on_animation_start'
    ]
    def __init__(self, **kwargs):
        super(MTWidget, self).__init__()

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
        kwargs.setdefault('inner_animation', ())

        self._id = None
        if 'id' in kwargs:
            self.id = kwargs.get('id')

        self._visible				= False
        self.animations				= []
        #self.draw_children          = kwargs.get('draw_children')

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
        for prop in kwargs.get('inner_animation'):
            kw = dict()
            if type(prop) in (list, tuple):
                prop, kw = prop
            self.enable_inner_animation(prop, **kw)

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

    '''
    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
    def _get_visible(self):
        return self._visible
    visible = property(_get_visible, _set_visible, doc='bool: visibility of widget')
    '''

    def apply_css(self, styles):
        '''Called at __init__ time to applied css attribute in current class.
        '''
        self.style.update(styles)

    def bring_to_front(self):
        '''Remove it from wherever it is and add it back at the top'''
        if self.parent:
            parent = self.parent
            print "p", self.parent
            parent.remove_widget(self)
            print "a", self.parent
            parent.add_widget(self)
            print "b", self.parent

    def hide(self):
        '''Hide the widget'''
        self.visible = False

    def show(self):
        '''Show the widget'''
        self.visible = True

    """
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
    """

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

# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
