'''
Colors: manipulate colors
'''

from OpenGL.GL import *

__all__ = ['set_color']

def set_color(*colors, **kwargs):
    '''Define current color to be used ::

        set_color(1, 0, 0, 1)
        drawLabel('Hello', pos=(100, 0))
        set_color(0, 1, 0, 1)
        drawLabel('World', pos=(200, 0))

    .. Note:
        Blending is activated if alpha value != 1

    :Parameters:
        `*colors` : list
            Can have 3 or 4 float value (between 0 and 1)
        `sfactor` : opengl factor, default to GL_SRC_ALPHA
            Default source factor to be used if blending is activated
        `dfactor` : opengl factor, default to GL_ONE_MINUS_SRC_ALPHA
            Default destination factor to be used if blending is activated
    '''

    kwargs.setdefault('sfactor', GL_SRC_ALPHA)
    kwargs.setdefault('dfactor', GL_ONE_MINUS_SRC_ALPHA)
    if len(colors) == 4:
        glColor4f(*colors)
        if colors[3] == 1:
            glDisable(GL_BLEND)
        else:
            glEnable(GL_BLEND)
            glBlendFunc(kwargs.get('sfactor'), kwargs.get('dfactor'))
    if len(colors) == 3:
        glColor3f(*colors)
        glDisable(GL_BLEND)

