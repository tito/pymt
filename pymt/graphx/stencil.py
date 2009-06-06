'''
Stencil: use stencil for mask drawing
'''

__all__ = [
    # stencil
    'GlStencil', 'gx_stencil',
    'stencilPush', 'stencilPop', 'stencilUse',
]

from pyglet import *
from pyglet.gl import *
from statement import *

### Stencil usage
stencil_stack = 0
def stencilGetStackLevel():
    global stencil_stack
    return stencil_stack

def stencilPush():
    '''Create a new stack in stencil stack.
    All the next draw will be done in stencil buffer until
    stencilUse() will be called.'''
    global stencil_stack
    glPushAttrib(GL_STENCIL_BUFFER_BIT | GL_STENCIL_TEST)
    stencil_stack += 1

    # enable stencil test if not yet enabled
    if not glIsEnabled(GL_STENCIL_TEST):
        glClearStencil(0)
        glClear(GL_STENCIL_BUFFER_BIT)
        glEnable(GL_STENCIL_TEST)

    # increment the draw buffer
    glStencilFunc(GL_NEVER, 0x0, 0x0)
    glStencilOp(GL_INCR, GL_INCR, GL_INCR)
    glColorMask(0, 0, 0, 0)

def stencilPop():
    '''Pop out the last stack from stencil stack'''
    global stencil_stack
    stencil_stack -=1
    glPopAttrib()

def stencilUse():
    '''Switch from stencil draw to color draw.
    Now, all drawing will be done on color buffer,
    using latest stencil stack.
    '''
    global stencil_stack
    glColorMask(1, 1, 1, 1)

    # draw inner content only when stencil match the buffer
    glStencilFunc(GL_EQUAL, stencil_stack, stencil_stack)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)


class GlStencil:
    '''Statement of stencilPush/stencilPop, designed to be use with "with" keyword

    Alias: gx_stencil.
    '''
    def __init__(self):
        pass

    def __enter__(self):
        stencilPush()

    def __exit__(self, type, value, traceback):
        stencilPop()

gx_stencil = GlStencil()
