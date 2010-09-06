'''
Graphx: acceleration module

This module should be not integrated inside accelerate module
Because it's loaded after OpenGL symbol are imported inside the main binary
Accelerate module is loaded at start, before any PyMT lib is used.
'''

# from the documentation http://docs.cython.org/src/tutorial/external.html
# filename in extern is only required for compiler.
# i (mathieu) have tested without filename, and seem work.
# if people don't have gl.h, we can even compile and use the symbol in runtime ?

# XXX cdef extern from "GL/gl.h":
cdef extern from "GL/gl.h":
    ctypedef float         GLfloat
    ctypedef unsigned int  GLenum
    cdef void glBegin(GLenum mode)
    cdef void glBlendFunc(GLenum src, GLenum dst)
    cdef void glDisable(GLenum mode)
    cdef void glEnable(GLenum mode)
    cdef void glEnd()
    cdef void glLineWidth(float)
    cdef void glPopAttrib()
    cdef void glPushAttrib(int)
    cdef void glVertex2f(GLfloat x, GLfloat y)
    cdef void glTexCoord2f(GLfloat x, GLfloat y)
    cdef void glColor4f(GLfloat r, GLfloat g, GLfloat b, GLfloat a)

cdef enum gldef:
    GL_QUADS            = 0x0007
    GL_LINE_BIT         = 0x00000004
    GL_BLEND            = 0x0BE2
    GL_DST_COLOR        = 0x0306
    GL_ONE_MINUS_SRC_ALPHA = 0x0303

def drawRectangle(GLenum style, float x, float y, float w, float h):
    glBegin(style)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def drawPolygon(GLenum style, list points, float linewidth):
    #points = _make_point_list(points)

    if linewidth > 0:
        glPushAttrib(GL_LINE_BIT)
        glLineWidth(linewidth)

    glBegin(style)
    for x, y in zip(points[::2], points[1::2]):
        glVertex2f(x, y)
    glEnd()

    if linewidth > 0:
        glPopAttrib()

def drawRectangleAlpha(GLenum style, float x, float y, float w, float h,
                       float a0, float a1, float a2, float a3):
    glEnable(GL_BLEND)
    glBlendFunc(GL_DST_COLOR, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(style)
    glColor4f(1, 1, 1, a0)
    glVertex2f(x, y)
    glColor4f(1, 1, 1, a1)
    glVertex2f(x + w, y)
    glColor4f(1, 1, 1, a2)
    glVertex2f(x + w, y + h)
    glColor4f(1, 1, 1, a3)
    glVertex2f(x, y + h)
    glEnd()
    glDisable(GL_BLEND)

def drawTexturedRectangle(float x, float y, float w, float h,
                          float t0, float t1, float t2, float t3,
                          float t4, float t5, float t6, float t7):
    glBegin(GL_QUADS)
    glTexCoord2f(t0, t1)
    glVertex2f(x, y)
    glTexCoord2f(t2, t3)
    glVertex2f(x + w, y)
    glTexCoord2f(t4, t5)
    glVertex2f(x + w, y + h)
    glTexCoord2f(t6, t7)
    glVertex2f(x, y + h)
    glEnd()


#def drawRoundedRectangle(float x, float y, float w, float h
