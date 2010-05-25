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
        super(MTAbstractLayout, self).__init__(**kwargs)

        self._animation_type    = kwargs.get('animation_type')
        self.animation_duration = kwargs.get('animation_duration')
        self.auto_layout        = kwargs.get('auto_layout')
        self.bg_color           = kwargs.get('bg_color')
        self.need_update        = False
        self.need_update_set    = False

        self.register_event_type('on_layout')


    def _set_animation_type(self, type):
        if type in AnimationAlpha.__dict__ :
            self._animation_type = type
        else:
            raise ValueError("'%s' is not a valid animation type! See http://pymt.txzone.net/wiki/index.php/DevGuide/EasingFunctions for a list of availabe easing functions!" % type)
    def _get_animation_type(self):
        return self._animation_type
    animation_type = property(_get_animation_type, _set_animation_type)

    def add_widget(self, widget, front=True, do_layout=None):
        super(MTAbstractLayout, self).add_widget(widget, front=front)
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
        layout = self.parent.get_parent_layout()
        if layout:
            self.push_handlers(on_layout=layout.update)

    def on_move(self, x, y):
        self.update()

    def on_resize(self, w, h):
        self.update()

    def on_update(self):
        if self.need_update:
            self.need_update = False
            self.do_layout()
        super(MTAbstractLayout, self).on_update()

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

    # overload all possible function that need to apply
    # relayout before accessing to the value
    def _get_size(self):
        if self.need_update and not self.need_update_set:
            self.need_update_set = True
            self.need_update = False
            self.do_layout()
            self.need_update_set = False
        return super(MTAbstractLayout, self)._get_size()
    size = property(_get_size, MTWidget._set_size)

    def _get_width(self):
        if self.need_update and not self.need_update_set:
            self.need_update_set = True
            self.need_update = False
            self.do_layout()
            self.need_update_set = False
        return super(MTAbstractLayout, self)._get_width()
    width = property(_get_width, MTWidget._set_width)

    def _get_height(self):
        if self.need_update and not self.need_update_set:
            self.need_update_set = True
            self.need_update = False
            self.do_layout()
            self.need_update_set = False
        return super(MTAbstractLayout, self)._get_height()
    height = property(_get_height, MTWidget._set_height)

    def _get_pos(self):
        if self.need_update and not self.need_update_set:
            self.need_update_set = True
            self.need_update = False
            self.do_layout()
            self.need_update_set = False
        return super(MTAbstractLayout, self)._get_pos()
    pos = property(_get_pos, MTWidget._set_pos)

    def _get_x(self):
        if self.need_update and not self.need_update_set:
            self.need_update_set = True
            self.need_update = False
            self.do_layout()
            self.need_update_set = False
        return super(MTAbstractLayout, self)._get_x()
    x = property(_get_x, MTWidget._set_x)

    def _get_y(self):
        if self.need_update and not self.need_update_set:
            self.need_update_set = True
            self.need_update = False
            self.do_layout()
            self.need_update_set = False
        return super(MTAbstractLayout, self)._get_y()
    y = property(_get_y, MTWidget._set_y)


