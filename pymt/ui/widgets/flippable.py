'''
Flippable Widget: This is wrapper widget using which you can make a widget have two sides and you can flip between the sides
'''

from __future__ import with_statement
__all__ = ['MTFlippableWidget']

from pyglet.gl import *
from ..factory import MTWidgetFactory
from ...graphx import gx_matrix, drawRectangle, set_color
from widget import MTWidget
from ..animation import Animation, AnimationAlpha

class MTFlippableWidget(MTWidget):
    ''' This is wrapper widget using which you can make a 
        widget have two sides and you can flip between the sides ::

        from pymt import *
        s = MTFlippableWidget()
        s.add_widget(MTLabel(label="Front"), side='front')
        s.add_widget(MTLabel(label="Back"), side='back')
        w = MTWindow()
        w.add_widget(s)
        @s.event
        def on_touch_down(touches, touchID, x, y):
            s.flip()
        runTouchApp()
        
    :Parameters:
        `side` : front or back, defaults to add to both sides
            This parameter tells which side to add the widget front or back.        
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
        self.bgcolor =(0.2,0.2,0.2)
        
    def add_widget(self, w, side='front', front=True):
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
            #Add to both
            self.add_widget(w, side='front', front=front)
            self.add_widget(w, side='back', front=front)

        try:
            w.parent = self
        except:
            pass

    def draw(self):
        with gx_matrix:
            set_color(*self.bgcolor)
            drawRectangle((0,0), (self.width, self.height))

    def flip_children(self):
        '''Flips the children
        this has to be called exactly half way through the animation
        so it looks like there are actually two sides'''
        if self.side == 'front':
            #Flip to back
            self.side = 'back'
            self.children = self.children_back
        else:
            self.side = 'front'
            self.children = self.children_front

    def flip_to(self, to):
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
