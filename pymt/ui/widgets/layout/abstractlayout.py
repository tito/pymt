'''
Abstract layout: layout base for implementation
'''
__all__ = ['MTAbstractLayout']

from ..widget import MTWidget
from ...animation import Animation, AnimationAlpha
from ....graphx import set_color, drawRectangle

class MTAbstractLayout(MTWidget):
    '''Abstract layout. Base class used to implement layout.

    :Property:
        `auto_layout` : bool, default to True
            Do layout when appropriate
        `animation_type` : str, default to None
            Specifies the easing function for animating the layout when it changes.
            Default is 'None', in which case no animation is performed at all.
            Any name of a valid AnuimationAlpha function can be used to turn on animation.
        `animation_time` : int, default to 1
            specifies the duration of the animations created when changing the layout (if any).

    :Events:
        `on_layout`
            Fired when layout function have been called
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractLayout:
            raise NotImplementedError, 'class MTAbstractLayout is abstract'

        kwargs.setdefault('size', (1,1)) #if standard size is bigger, tehn stretching does work, if other things are smaller tahn teh defautl(100,100)
        kwargs.setdefault('size_hint', (1,1)) #layouts automatically stretch themselves if inside another layout
        kwargs.setdefault('auto_layout', True)
        kwargs.setdefault('animation_type', None)
        kwargs.setdefault('animation_duration', 1)
        kwargs.setdefault('bg_color', (0,0,0,0)) #good for debugging layout

        self._minimum_size = (1,1)

        super(MTAbstractLayout, self).__init__(**kwargs)

        self._animation_type    = kwargs.get('animation_type')
        self.animation_duration = kwargs.get('animation_duration')
        self.auto_layout        = kwargs.get('auto_layout')
        self.bg_color           = kwargs.get('bg_color')
        self.need_update        = False
        self.need_update_set    = False


        self.register_event_type('on_layout')


    def _get_minimum_size(self):
        return self._minimum_size
    def _set_minimum_size(self, size):
        self._minimum_size = size
        if self.width < size [0]:
            self.width = size[0]
        if self.height < size[1]:
            self.height = size[1]
    minimum_size = property(_get_minimum_size, _set_minimum_size)

    def _set_animation_type(self, type):
        if type in AnimationAlpha.__dict__ :
            self._animation_type = type
        else:
            raise ValueError("'%s' is not a valid animation type! See http://pymt.eu/wiki/DevGuide/EasingFunctions for a list of availabe easing functions!" % type)
    def _get_animation_type(self):
        return self._animation_type
    animation_type = property(_get_animation_type, _set_animation_type)

    def add_widget(self, widget, front=True, do_layout=None):
        super(MTAbstractLayout, self).add_widget(widget, front=front)
        self.update_minimum_size()
        if do_layout or (not do_layout and self.auto_layout):
            self.need_update = True

    def remove_widget(self, widget, do_layout=None):
        super(MTAbstractLayout, self).remove_widget(widget)
        self.need_layout = True
        if do_layout or (not do_layout and self.auto_layout):
            self.need_update = True

    def reposition_child(self, child, **kwargs):
        if self.animation_type and len(kwargs):
            kwargs['f'] = self.animation_type
            kwargs['d'] = self.animation_duration
            child.do(Animation(**kwargs))
        else:
            for prop in kwargs:
                child.__setattr__(prop, kwargs[prop])

    def get_parent_layout(self):
        return self

    def on_parent(self):
        if not self.parent:
            return

    def update_minimum_size(self):
        self.minimum_size = self.size

    def on_move(self, x, y):
        self.update()

    def on_resize(self, w, h):
        self.width = max(w, self.minimum_size[0])
        self.height = max(h, self.minimum_size[1])

        self.update()

    def on_update(self):
        super(MTAbstractLayout, self).on_update()
        if self.need_update:
            self.need_update = False
            self.update_minimum_size()
            self.do_layout()

    def update(self):
        self.need_update = True


    def on_layout(self):
        pass

    def do_layout(self):
        for w in self.children:
            w.pos = self.pos
            if w.size_hint[0]:
                w.width = w.size_hint[0]*self.width
            if w.size_hint[1]:
                w.height = w.size_hint[1]*self.height
