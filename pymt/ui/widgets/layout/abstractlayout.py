'''
Abstract layout: layout base for implementation
'''
__all__ = ['MTAbstractLayout']

from ..widget import MTWidget
from ...animation import Animation, AnimationAlpha

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
        
        kwargs.setdefault('auto_layout', True)
        kwargs.setdefault('animation_type', None)
        kwargs.setdefault('animation_duration', 1)
        super(MTAbstractLayout, self).__init__(**kwargs)

        self._animation_type    = kwargs.get('animation_type')
        self.animation_duration = kwargs.get('animation_duration')
        self.auto_layout        = kwargs.get('auto_layout')

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
            self.do_layout()

    def remove_widget(self, widget, do_layout=None):
        super(MTAbstractLayout, self).remove_widget(widget)
        self.need_layout = True
        if do_layout or (not do_layout and self.auto_layout):
            self.do_layout()
        
    def reposition_child(self, child, **kwargs):
        if self.animation_type and len(kwargs):
            kwargs['f'] = self.animation_type
            kwargs['d'] = self.animation_duration
            child.do(Animation(**kwargs))
        else:
            for prop in kwargs:
                child.__setattr__(prop, kwargs[prop])

    def do_layout(self):
        pass

    def get_parent_layout(self):
        return self

    def on_layout(self):
        pass
    
    