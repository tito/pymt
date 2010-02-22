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
        `on_content_resize`
            Fired when content_width or content_height have changed
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractLayout:
            raise NotImplementedError, 'class MTAbstractLayout is abstract'
        
        kwargs.setdefault('auto_layout', True)
        kwargs.setdefault('animation_type', None)
        kwargs.setdefault('animation_duration', 1)
        super(MTAbstractLayout, self).__init__(**kwargs)
        
        self.register_event_type('on_layout')
        self.register_event_type('on_content_resize')
        self.auto_layout        = kwargs.get('auto_layout')
        self.need_layout        = False
        self.need_parent_layout = False
        self._content_height    = 0
        self._content_width     = 0
        self._animation_type    = kwargs.get('animation_type')
        self.animation_duration = kwargs.get('animation_duration')
        
        self.push_handlers(on_parent_resize=self.require_layout)
        
        
    def on_parent(self):
        pl = self.parent.get_parent_layout()
        if pl and pl != self:
            def update_me(*args):
                self.do_layout()
            pl.push_handlers(on_layout=update_me)


    def _set_animation_type(self, type):
        if type in AnimationAlpha.__dict__ :
            self._animation_type = type
        else:
            raise ValueError("'%s' is not a valid animation type! See http://pymt.txzone.net/wiki/index.php/DevGuide/EasingFunctions for a list of availabe easing functions!" % type)
    def _get_animation_type(self):
        return self._animation_type
    animation_type = property(_get_animation_type, _set_animation_type)

    def _set_content_width(self, w):
        if self._content_width == w:
            return
        self._content_width = w
        self.dispatch_event('on_content_resize', self._content_width, self._content_height)
    def _get_content_width(self):
        return self._content_width
    content_width = property(_get_content_width, _set_content_width)

    def _set_content_height(self, w):
        if self._content_height == w:
            return
        self._content_height = w
        self.dispatch_event('on_content_resize', self._content_height, self._content_height)
    def _get_content_height(self):
        return self._content_height
    content_height = property(_get_content_height, _set_content_height)

    def _set_content_size(self, size):
        w, h = size
        if self._content_width == w and self._content_height == h:
            return
        self._content_width = w
        self._content_height = h
        self.dispatch_event('on_content_resize', self._content_width, self._content_height)
    def _get_content_size(self):
        return (self.content_width, self.content_height)
    content_size = property(_get_content_size, _set_content_size)

    def add_widget(self, widget, front=True, do_layout=None):
        super(MTAbstractLayout, self).add_widget(widget, front=front)
        self.need_layout = True
        if do_layout or (not do_layout and self.auto_layout):
            self.do_layout()

    def remove_widget(self, widget, do_layout=None):
        super(MTAbstractLayout, self).remove_widget(widget)
        self.need_layout = True
        if do_layout or (not do_layout and self.auto_layout):
            self.do_layout()

    def do_layout(self):
        self.need_layout = False

    def do_parent_layout(self):
        self.need_parent_layout = False
        if self.parent:
            layout = self.parent.get_parent_layout()
            if layout:
                layout.do_layout()
                
    def reposition_child(self, child, **kwargs):
        if self.animation_type and len(kwargs):
            kwargs['f'] = self.animation_type
            kwargs['d'] = self.animation_duration
            child.do(Animation(**kwargs))
        else:
            for prop in kwargs:
                child.__setattr__(prop, kwargs[prop])

    
    def require_layout(self, *args):
        '''Will require the layout to be updated. i.e. sets need_layout , and then calls self.update(if autoupdate is on).
            :Arguments:
                `*args`,takes any number of arguments.  None of them are used, but this method can easily be attached as an event handler to require layout in response to certain events
        ''' 
        self.need_layout = True
        if self.auto_layout:
            self.update()


    def update(self):
        if self.need_parent_layout:
            self.do_parent_layout()
        if self.need_layout:
            self.do_layout()

       
    def get_parent_layout(self):
        return self

    def on_layout(self):
        pass

    def on_content_resize(self, w, h):
        self.need_parent_layout = True
        if self.auto_layout:
            self.do_parent_layout()

    def on_move(self, x, y):
        self.need_layout = True
        if self.auto_layout:
            self.do_layout()
            super(MTAbstractLayout, self).on_move(x, y)

