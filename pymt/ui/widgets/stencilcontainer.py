'''
Stencil container: clip drawing of children to his container
'''

__all__ = ['MTStencilContainer']

from pyglet.gl import *
from widget import MTWidget
from ...graphx import drawRectangle, gx_stencil, stencilUse
from ..factory import MTWidgetFactory

stencil_stack = 0

class MTStencilContainer(MTWidget):
    '''This container clip the children drawing to his
    container ::

        from pymt import *
        s = MTStencilContainer(size=(200, 200))
        s.add_widget(MTLabel(label="plop", pos=(100, 100), font_size=16))
        s.add_widget(MTLabel(label="a very very long sentence !", pos=(100, 150), font_size=16))
        w = MTWindow()
        w.add_widget(s)
        runTouchApp()
    '''
    def __init__(self, **kwargs):
        super(MTStencilContainer, self).__init__(**kwargs)

    def on_draw(self):
        with gx_stencil:
            # draw on stencil
            drawRectangle(pos=self.pos, size=self.size)

            # switch drawing to color buffer.
            stencilUse()

            # draw childrens
            for w in self.children:
                w.dispatch_event('on_draw')

# Register all base widgets
MTWidgetFactory.register('MTStencilContainer', MTStencilContainer)
