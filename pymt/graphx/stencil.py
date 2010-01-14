'''
Stencil: use stencil for mask drawing

Usage ::

    with gx_stencil:
        # change viewport
        # draw stuff

'''

__all__ = [
    # stencil
    'GlStencil', 'gx_stencil',
    'stencilPush', 'stencilPop', 'stencilUse',
]

from OpenGL.GL import *
from statement import *

### Stencil usage
stencil_stack       = 0
stencil_stack_dl    = []
stencil_stack_view  = []
def stencilGetStackLevel():
    global stencil_stack
    return stencil_stack

def stencilPush():
    '''Create a new stack in stencil stack.
    All the next draw will be done in stencil buffer until
    stencilUse() will be called.'''
    global stencil_stack, stencil_stack_dl, stencil_stack_view
    glPushAttrib(GL_STENCIL_BUFFER_BIT | GL_STENCIL_TEST)

    # enable stencil test if not yet enabled
    if not glIsEnabled(GL_STENCIL_TEST):
        glClearStencil(0)
        glClear(GL_STENCIL_BUFFER_BIT)
        glEnable(GL_STENCIL_TEST)

    # increment the draw buffer
    glStencilFunc(GL_NEVER, 0x0, 0x0)
    glStencilOp(GL_INCR, GL_INCR, GL_INCR)
    glColorMask(0, 0, 0, 0)

    # save model view
    m = glGetFloatv(GL_MODELVIEW_MATRIX)
    stencil_stack_view.append(m)

    # start recording GL operation
    dl = GlDisplayList()
    dl.start()
    stencil_stack_dl.append(dl)

    stencil_stack += 1

def stencilPop():
    '''Pop out the last stack from stencil stack'''
    global stencil_stack, stencil_stack_dl, stencil_stack_view
    glPopAttrib()
    stencil_stack -=1

    # remove current stencil stack
    stencil_stack_dl.pop()
    stencil_stack_view.pop()

    # replay stencil stack from the start
    # only if it's enabled
    if not glIsEnabled(GL_STENCIL_TEST):
        return

    # clear stencil
    glClearStencil(0)
    glClear(GL_STENCIL_BUFFER_BIT)

    # increment the draw buffer
    glStencilFunc(GL_NEVER, 0x0, 0x0)
    glStencilOp(GL_INCR, GL_INCR, GL_INCR)
    glColorMask(0, 0, 0, 0)

    # replay all gl operation
    for idx in xrange(stencil_stack):
        dl = stencil_stack_dl[idx]
        view = stencil_stack_view[idx]
        with gx_matrix_identity:
            glMultMatrixf(view)
            dl.draw()

    # draw inner content only when stencil match the buffer
    glColorMask(1, 1, 1, 1)
    glStencilFunc(GL_EQUAL, stencil_stack, stencil_stack)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

def stencilUse():
    '''Switch from stencil draw to color draw.
    Now, all drawing will be done on color buffer,
    using latest stencil stack.
    '''
    global stencil_stack, stencil_stack_dl

    # stop recording gl operation
    stencil_stack_dl[stencil_stack-1].stop()
    stencil_stack_dl[stencil_stack-1].draw()

    # draw inner content only when stencil match the buffer
    glColorMask(1, 1, 1, 1)
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

#: Alias to GlStencil()
gx_stencil = GlStencil()
