'''
Stencil container: A widget that clip drawing of children to his container
'''

__all__ = ['MTStencilContainer']

from pyglet.gl import *
from widget import MTWidget
from ...graphx import drawRectangle
from ..factory import MTWidgetFactory

class MTStencilContainer(MTWidget):
    '''This container clip the children drawing to his container ::

        from pymt import *
        s = MTStencilContainer(size=(200, 200))
        s.add_widget(MTLabel(text="plop", pos=(100, 100), font_size=16))
        s.add_widget(MTLabel(text="a very very long sentence !", pos=(100, 150), font_size=16))
        w = MTWindow()
        w.add_widget(s)
        runTouchApp()
    '''
    def __init__(self, **kwargs):
        super(MTStencilContainer, self).__init__(**kwargs)

    def on_draw(self):
        # enable stencil test
        glClearStencil(0)
        glClear(GL_STENCIL_BUFFER_BIT)
        glEnable(GL_STENCIL_TEST)
        glStencilFunc(GL_NEVER, 0x0, 0x0)
        glStencilOp(GL_INCR, GL_INCR, GL_INCR)

        drawRectangle(pos=self.pos, size=self.size)

        # draw inner content
        glStencilFunc(GL_EQUAL, 0x1, 0x1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

        # TODO optimize container to draw only children that match bbox
        for w in self.children:
            w.dispatch_event('on_draw')

        glDisable(GL_STENCIL_TEST)



# Register all base widgets
MTWidgetFactory.register('MTStencilContainer', MTStencilContainer)
