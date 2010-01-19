'''
Flippable Widget: A widget with 2 sides who can flip between the sides.
'''


__all__ = ['MTFlippableWidget']

from OpenGL.GL import *
from ..factory import MTWidgetFactory
from ...graphx import gx_matrix, drawCSSRectangle, set_color
from widget import MTWidget
from ..animation import Animation, AnimationAlpha

class MTFlippableWidget(MTWidget):
    '''This is wrapper widget using which you can make a
    widget have two sides and you can flip between the sides ::

        from pymt import *
        s = MTFlippableWidget()
        s.add_widget(MTLabel(label="Front"), side='front')
        s.add_widget(MTLabel(label="Back"), side='back')
        w = MTWindow()
        w.add_widget(s)
        @s.event
        def on_touch_down(touch):
            s.flip()
        runTouchApp()

    '''
    def __init__(self, **kwargs):
        super(MTFlippableWidget, self).__init__(**kwargs)

        # For flipping animations
        self.zangle = 0
        self.side = 'front'

        # Holds children for both sides
        self.children_front = []
        self.children_back = []
        self.children = self.children_front

        self.anim = Animation(self, 'flip', 'zangle', 180, 1, 10, func=AnimationAlpha.ramp)

    def add_widget(self, w, side='front', front=True):
        '''Add a widget on a side.

        :Parameters:
            `front` : boolean, default is True
                Indicate if the widget must be top added or bottom added in the list.
            `side` : string, default is 'front'
                Specify which side you want to add widget.
                (can be one of 'front', 'back' or '', defaults to add to both sides)
        '''
        if side == 'front':
            if front:
                self.children_front.append(w)
            else:
                self.children_front.insert(0, w)
        elif side == 'back':
            if front:
                self.children_back.append(w)
            else:
                self.children_back.insert(0, w)
        else:
            self.add_widget(w, side='front', front=front)
            self.add_widget(w, side='back', front=front)

        try:
            w.parent = self
        except:
            pass

    def draw(self):
        with gx_matrix:
            set_color(self.style.get('bg-color'))
            drawCSSRectangle(pos=(0,0), size=self.size, style=self.style)

    def flip_children(self):
        # This has to be called exactly half way through the animation
        # so it looks like there are actually two sides'''
        if self.side == 'front':
            self.side = 'back'
            self.children = self.children_back
        else:
            self.side = 'front'
            self.children = self.children_front

    def flip_to(self, to):
        '''Flip to the requested side ('front' or 'back')'''
        if to == 'back' and self.side == 'front':
            self.flip_children()
        elif to == 'front' and self.side == 'back':
            self.flip_children()

    def flip(self):
       '''Triggers a flipping animation'''
       if self.side == 'front':
           self.anim.value_to = 180
       else:
           self.anim.value_to = 0
       self.anim.reset()
       self.anim.start()

    def on_draw(self):
        if self.zangle < 90:
            self.flip_to('front')
        else:
            self.flip_to('back')
        with gx_matrix:
            glTranslatef(self.x, self.y, 0)
            glTranslatef(self.width / 2, 0, 0)
            if self.side == 'front':
                glRotatef(self.zangle, 0, 1, 0)
            else:
                glRotatef(self.zangle + 180, 0, 1, 0)
            glTranslatef(-self.width / 2, 0, 0)
            super(MTFlippableWidget, self).on_draw()

 # Register all base widgets
MTWidgetFactory.register('MTFlippableWidget', MTFlippableWidget)
