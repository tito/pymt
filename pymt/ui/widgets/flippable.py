'''
Flippable Widget: A widget with 2 sides who can flip between the sides.
'''


__all__ = ('MTFlippableWidget', )

from OpenGL.GL import glTranslatef, glRotatef
from pymt.graphx import gx_matrix, drawCSSRectangle, set_color
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.animation import Animation
from pymt.utils import SafeList

class MTFlippableWidget(MTWidget):
    '''This is wrapper widget using which you can make a
    widget have two sides and you can flip between the sides ::

        from pymt import *

        widget = MTFlippableWidget()
        widget.add_widget(MTLabel(label='Front'), side='front')
        widget.add_widget(MTLabel(label='Back'), side='back')

        @widget.event
        def on_touch_down(touch):
            widget.flip()

        runTouchApp(widget)

    :Parameters:
        `flipangle` : float, default to 90.
            Angle to flip back/front

    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('flipangle', 90.)
        super(MTFlippableWidget, self).__init__(**kwargs)
        self.flipangle      = kwargs.get('flipangle')

        # For flipping animations
        self.zangle         = 0
        self.side           = 'front'

        # Holds children for both sides
        self.children_front = SafeList()
        self.children_back  = SafeList()

        self._anim_current  = None
        self._anim_back     = Animation(zangle=180)
        self._anim_front    = Animation(zangle=0)

    def add_widget(self, w, side='front', front=True):
        '''Add a widget on a side.

        :Parameters:
            `front` : boolean, default is True
                Indicate if the widget must be top added or bottom added in the list.
            `side` : string, default is 'front'
                Specify which side you want to add widget.
                (can be one of 'front', 'back' or '', defaults to add to both sides)
        '''
        assert(side in ('front', 'back', ''))
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

        if self.side == side:
            super(MTFlippableWidget, self).add_widget(w, front)

        try:
            w.parent = self
        except Exception:
            pass

    def draw(self):
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=(0, 0), size=self.size, style=self.style)

    def _flip_children(self):
        # This has to be called exactly half way through the animation
        # so it looks like there are actually two sides'''
        if self.side == 'front':
            self.side = 'back'
            self.children.clear()
            for x in self.children_back[:]:
                super(MTFlippableWidget, self).add_widget(x)
        else:
            self.side = 'front'
            self.children.clear()
            for x in self.children_front[:]:
                super(MTFlippableWidget, self).add_widget(x)

    def _set_side(self, to):
        assert(to in ('back', 'front'))
        if to == 'back' and self.side == 'front':
            self._flip_children()
        elif to == 'front' and self.side == 'back':
            self._flip_children()

    def flip_to(self, to):
        '''Flip to the requested side ('front' or 'back')'''
        assert(to in ('back', 'front'))
        if to == 'back' and self.side == 'front':
            self.flip()
        elif to == 'front' and self.side == 'back':
            self.flip()

    def flip(self):
        '''Triggers a flipping animation'''
        if self._anim_current:
            self._anim_current.stop()
        if self.side == 'front':
            self._anim_current = self.do(self._anim_back)
        else:
            self._anim_current = self.do(self._anim_front)

    def on_update(self):
        if self.zangle < self.flipangle:
            self._set_side('front')
        else:
            self._set_side('back')
        return super(MTFlippableWidget, self).on_update()

    def on_draw(self):
        with gx_matrix:
            glTranslatef(self.x, self.y, 0)
            glTranslatef(self.width / 2, 0, 0)
            if self.side == 'front':
                glRotatef(self.zangle, 0, 1, 0)
            else:
                glRotatef(self.zangle + 180, 0, 1, 0)
            glTranslatef(-self.width / 2, 0, 0)
            super(MTFlippableWidget, self).on_draw()
