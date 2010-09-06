'''
Stencil: use stencil for mask drawing

Usage ::

    with gx_stencil:
        # change viewport
        # draw stuff

'''

__all__ = (
    # stencil
    'GlStencil', 'gx_stencil',
    'stencilPush', 'stencilPop', 'stencilUse',
)

from OpenGL.GL import GL_STENCIL_BUFFER_BIT, GL_STENCIL_TEST, \
        GL_NEVER, GL_INCR, GL_MODELVIEW_MATRIX, GL_EQUAL, GL_KEEP, \
        glColorMask, glPushAttrib, glPopAttrib, glIsEnabled, \
        glEnable, glStencilOp, glStencilFunc, \
        glClear, glClearStencil, glMultMatrixf, glGetFloatv
from pymt.graphx.statement import gx_matrix_identity, GlDisplayList

### Stencil usage
__stencil_stack       = 0
__stencil_stack_dl    = []
__stencil_stack_view  = []
def stencilGetStackLevel():
    return __stencil_stack

def stencilPush():
    '''Create a new stack in stencil stack.
    All the next draw will be done in stencil buffer until
    stencilUse() will be called.'''
    global __stencil_stack
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
    __stencil_stack_view.append(m)

    # start recording GL operation
    dl = GlDisplayList()
    dl.start()
    __stencil_stack_dl.append(dl)

    __stencil_stack += 1

def stencilPop():
    '''Pop out the last stack from stencil stack'''
    global __stencil_stack
    glPopAttrib()
    __stencil_stack -= 1

    # remove current stencil stack
    __stencil_stack_dl.pop()
    __stencil_stack_view.pop()

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
    for idx in xrange(__stencil_stack):
        dl = __stencil_stack_dl[idx]
        view = __stencil_stack_view[idx]
        with gx_matrix_identity:
            glMultMatrixf(view)
            dl.draw()

    # draw inner content only when stencil match the buffer
    glColorMask(1, 1, 1, 1)
    glStencilFunc(GL_EQUAL, __stencil_stack, __stencil_stack)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

def stencilUse():
    '''Switch from stencil draw to color draw.
    Now, all drawing will be done on color buffer,
    using latest stencil stack.
    '''
    # stop recording gl operation
    __stencil_stack_dl[__stencil_stack-1].stop()
    __stencil_stack_dl[__stencil_stack-1].draw()

    # draw inner content only when stencil match the buffer
    glColorMask(1, 1, 1, 1)
    glStencilFunc(GL_EQUAL, __stencil_stack, __stencil_stack)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

class GlStencil:
    '''Statement of stencilPush/stencilPop, designed to be use with
    "with" keyword.

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
