# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

cdef extern from "GL/gl.h":
    ctypedef unsigned int        GLenum
    ctypedef unsigned char  GLboolean
    ctypedef unsigned int        GLbitfield
    ctypedef void                        GLvoid
    ctypedef signed char    GLbyte
    ctypedef short                    GLshort
    ctypedef int                        GLint
    ctypedef unsigned char  GLubyte
    ctypedef unsigned short    GLushort
    ctypedef unsigned int        GLuint
    ctypedef int                        GLsizei
    ctypedef float                    GLfloat
    ctypedef float                    GLclampf
    ctypedef double                    GLdouble
    ctypedef double                    GLclampd
    ctypedef char                     GLchar
    ctypedef unsigned int   GLhandleARB

    cdef void glClearIndex(GLfloat c)
    cdef void glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
    cdef void glClear(GLbitfield mask)
    cdef void glIndexMask(GLuint mask)
    cdef void glColorMask(GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha)
    cdef void glAlphaFunc(GLenum func, GLclampf ref)
    cdef void glBlendFunc(GLenum sfactor, GLenum dfactor)
    cdef void glLogicOp(GLenum opcode)
    cdef void glCullFace(GLenum mode)
    cdef void glFrontFace(GLenum mode)
    cdef void glPointSize(GLfloat size)
    cdef void glLineWidth(GLfloat width)
    cdef void glLineStipple(GLint factor, GLushort pattern)
    cdef void glPolygonMode(GLenum face, GLenum mode)
    cdef void glPolygonOffset(GLfloat factor, GLfloat units)
    cdef void glPolygonStipple(GLubyte *mask)
    cdef void glGetPolygonStipple(GLubyte *mask)
    cdef void glEdgeFlag(GLboolean flag)
    cdef void glEdgeFlagv(GLboolean *flag)
    cdef void glScissor(GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glClipPlane(GLenum plane, GLdouble *equation)
    cdef void glGetClipPlane(GLenum plane, GLdouble *equation)
    cdef void glDrawBuffer(GLenum mode)
    cdef void glReadBuffer(GLenum mode)
    cdef void glEnable(GLenum cap)
    cdef void glDisable(GLenum cap)
    cdef GLboolean glIsEnabled(GLenum cap)
    cdef void glEnableClientState(GLenum cap)
    cdef void glDisableClientState(GLenum cap)
    cdef void glGetBooleanv(GLenum pname, GLboolean *params)
    cdef void glGetDoublev(GLenum pname, GLdouble *params)
    cdef void glGetFloatv(GLenum pname, GLfloat *params)
    cdef void glGetIntegerv(GLenum pname, GLint *params)
    cdef void glPushAttrib(GLbitfield mask)
    cdef void glPopAttrib()
    cdef void glPushClientAttrib(GLbitfield mask)
    cdef void glPopClientAttrib()
    cdef GLint glRenderMode(GLenum mode)
    cdef GLenum glGetError()
    cdef GLubyte* glGetString(GLenum name)
    cdef void glFinish()
    cdef void glFlush()
    cdef void glHint(GLenum target, GLenum mode)
    cdef void glClearDepth(GLclampd depth)
    cdef void glDepthFunc(GLenum func)
    cdef void glDepthMask(GLboolean flag)
    cdef void glDepthRange(GLclampd near_val, GLclampd far_val)
    cdef void glClearAccum(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
    cdef void glAccum(GLenum op, GLfloat value)
    cdef void glMatrixMode(GLenum mode)
    cdef void glOrtho(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top, GLdouble near_val, GLdouble far_val)
    cdef void glFrustum(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top, GLdouble near_val, GLdouble far_val)
    cdef void glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glPushMatrix()
    cdef void glPopMatrix()
    cdef void glLoadIdentity()
    cdef void glLoadMatrixd(GLdouble *m)
    cdef void glLoadMatrixf(GLfloat *m)
    cdef void glMultMatrixd(GLdouble *m)
    cdef void glMultMatrixf(GLfloat *m)
    cdef void glRotated(GLdouble angle, GLdouble x, GLdouble y, GLdouble z)
    cdef void glRotatef(GLfloat angle, GLfloat x, GLfloat y, GLfloat z)
    cdef void glScaled(GLdouble x, GLdouble y, GLdouble z)
    cdef void glScalef(GLfloat x, GLfloat y, GLfloat z)
    cdef void glTranslated(GLdouble x, GLdouble y, GLdouble z)
    cdef void glTranslatef(GLfloat x, GLfloat y, GLfloat z)
    cdef GLboolean glIsList(GLuint list)
    cdef void glDeleteLists(GLuint list, GLsizei range)
    cdef GLuint glGenLists(GLsizei range)
    cdef void glNewList(GLuint list, GLenum mode)
    cdef void glEndList()
    cdef void glCallList(GLuint list)
    cdef void glCallLists(GLsizei n, GLenum type, GLvoid *lists)
    cdef void glListBase(GLuint base)
    cdef void glBegin(GLenum mode)
    cdef void glEnd()
    cdef void glVertex2d(GLdouble x, GLdouble y)
    cdef void glVertex2f(GLfloat x, GLfloat y)
    cdef void glVertex2i(GLint x, GLint y)
    cdef void glVertex2s(GLshort x, GLshort y)
    cdef void glVertex3d(GLdouble x, GLdouble y, GLdouble z)
    cdef void glVertex3f(GLfloat x, GLfloat y, GLfloat z)
    cdef void glVertex3i(GLint x, GLint y, GLint z)
    cdef void glVertex3s(GLshort x, GLshort y, GLshort z)
    cdef void glVertex4d(GLdouble x, GLdouble y, GLdouble z, GLdouble w)
    cdef void glVertex4f(GLfloat x, GLfloat y, GLfloat z, GLfloat w)
    cdef void glVertex4i(GLint x, GLint y, GLint z, GLint w)
    cdef void glVertex4s(GLshort x, GLshort y, GLshort z, GLshort w)
    cdef void glVertex2dv(GLdouble *v)
    cdef void glVertex2fv(GLfloat *v)
    cdef void glVertex2iv(GLint *v)
    cdef void glVertex2sv(GLshort *v)
    cdef void glVertex3dv(GLdouble *v)
    cdef void glVertex3fv(GLfloat *v)
    cdef void glVertex3iv(GLint *v)
    cdef void glVertex3sv(GLshort *v)
    cdef void glVertex4dv(GLdouble *v)
    cdef void glVertex4fv(GLfloat *v)
    cdef void glVertex4iv(GLint *v)
    cdef void glVertex4sv(GLshort *v)
    cdef void glNormal3b(GLbyte nx, GLbyte ny, GLbyte nz)
    cdef void glNormal3d(GLdouble nx, GLdouble ny, GLdouble nz)
    cdef void glNormal3f(GLfloat nx, GLfloat ny, GLfloat nz)
    cdef void glNormal3i(GLint nx, GLint ny, GLint nz)
    cdef void glNormal3s(GLshort nx, GLshort ny, GLshort nz)
    cdef void glNormal3bv(GLbyte *v)
    cdef void glNormal3dv(GLdouble *v)
    cdef void glNormal3fv(GLfloat *v)
    cdef void glNormal3iv(GLint *v)
    cdef void glNormal3sv(GLshort *v)
    cdef void glIndexd(GLdouble c)
    cdef void glIndexf(GLfloat c)
    cdef void glIndexi(GLint c)
    cdef void glIndexs(GLshort c)
    cdef void glIndexub(GLubyte c)
    cdef void glIndexdv(GLdouble *c)
    cdef void glIndexfv(GLfloat *c)
    cdef void glIndexiv(GLint *c)
    cdef void glIndexsv(GLshort *c)
    cdef void glIndexubv(GLubyte *c)
    cdef void glColor3b(GLbyte red, GLbyte green, GLbyte blue)
    cdef void glColor3d(GLdouble red, GLdouble green, GLdouble blue)
    cdef void glColor3f(GLfloat red, GLfloat green, GLfloat blue)
    cdef void glColor3i(GLint red, GLint green, GLint blue)
    cdef void glColor3s(GLshort red, GLshort green, GLshort blue)
    cdef void glColor3ub(GLubyte red, GLubyte green, GLubyte blue)
    cdef void glColor3ui(GLuint red, GLuint green, GLuint blue)
    cdef void glColor3us(GLushort red, GLushort green, GLushort blue)
    cdef void glColor4b(GLbyte red, GLbyte green, GLbyte blue, GLbyte alpha)
    cdef void glColor4d(GLdouble red, GLdouble green, GLdouble blue, GLdouble alpha)
    cdef void glColor4f(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
    cdef void glColor4i(GLint red, GLint green, GLint blue, GLint alpha)
    cdef void glColor4s(GLshort red, GLshort green, GLshort blue, GLshort alpha)
    cdef void glColor4ub(GLubyte red, GLubyte green, GLubyte blue, GLubyte alpha)
    cdef void glColor4ui(GLuint red, GLuint green, GLuint blue, GLuint alpha)
    cdef void glColor4us(GLushort red, GLushort green, GLushort blue, GLushort alpha)
    cdef void glColor3bv(GLbyte *v)
    cdef void glColor3dv(GLdouble *v)
    cdef void glColor3fv(GLfloat *v)
    cdef void glColor3iv(GLint *v)
    cdef void glColor3sv(GLshort *v)
    cdef void glColor3ubv(GLubyte *v)
    cdef void glColor3uiv(GLuint *v)
    cdef void glColor3usv(GLushort *v)
    cdef void glColor4bv(GLbyte *v)
    cdef void glColor4dv(GLdouble *v)
    cdef void glColor4fv(GLfloat *v)
    cdef void glColor4iv(GLint *v)
    cdef void glColor4sv(GLshort *v)
    cdef void glColor4ubv(GLubyte *v)
    cdef void glColor4uiv(GLuint *v)
    cdef void glColor4usv(GLushort *v)
    cdef void glTexCoord1d(GLdouble s)
    cdef void glTexCoord1f(GLfloat s)
    cdef void glTexCoord1i(GLint s)
    cdef void glTexCoord1s(GLshort s)
    cdef void glTexCoord2d(GLdouble s, GLdouble t)
    cdef void glTexCoord2f(GLfloat s, GLfloat t)
    cdef void glTexCoord2i(GLint s, GLint t)
    cdef void glTexCoord2s(GLshort s, GLshort t)
    cdef void glTexCoord3d(GLdouble s, GLdouble t, GLdouble r)
    cdef void glTexCoord3f(GLfloat s, GLfloat t, GLfloat r)
    cdef void glTexCoord3i(GLint s, GLint t, GLint r)
    cdef void glTexCoord3s(GLshort s, GLshort t, GLshort r)
    cdef void glTexCoord4d(GLdouble s, GLdouble t, GLdouble r, GLdouble q)
    cdef void glTexCoord4f(GLfloat s, GLfloat t, GLfloat r, GLfloat q)
    cdef void glTexCoord4i(GLint s, GLint t, GLint r, GLint q)
    cdef void glTexCoord4s(GLshort s, GLshort t, GLshort r, GLshort q)
    cdef void glTexCoord1dv(GLdouble *v)
    cdef void glTexCoord1fv(GLfloat *v)
    cdef void glTexCoord1iv(GLint *v)
    cdef void glTexCoord1sv(GLshort *v)
    cdef void glTexCoord2dv(GLdouble *v)
    cdef void glTexCoord2fv(GLfloat *v)
    cdef void glTexCoord2iv(GLint *v)
    cdef void glTexCoord2sv(GLshort *v)
    cdef void glTexCoord3dv(GLdouble *v)
    cdef void glTexCoord3fv(GLfloat *v)
    cdef void glTexCoord3iv(GLint *v)
    cdef void glTexCoord3sv(GLshort *v)
    cdef void glTexCoord4dv(GLdouble *v)
    cdef void glTexCoord4fv(GLfloat *v)
    cdef void glTexCoord4iv(GLint *v)
    cdef void glTexCoord4sv(GLshort *v)
    cdef void glRasterPos2d(GLdouble x, GLdouble y)
    cdef void glRasterPos2f(GLfloat x, GLfloat y)
    cdef void glRasterPos2i(GLint x, GLint y)
    cdef void glRasterPos2s(GLshort x, GLshort y)
    cdef void glRasterPos3d(GLdouble x, GLdouble y, GLdouble z)
    cdef void glRasterPos3f(GLfloat x, GLfloat y, GLfloat z)
    cdef void glRasterPos3i(GLint x, GLint y, GLint z)
    cdef void glRasterPos3s(GLshort x, GLshort y, GLshort z)
    cdef void glRasterPos4d(GLdouble x, GLdouble y, GLdouble z, GLdouble w)
    cdef void glRasterPos4f(GLfloat x, GLfloat y, GLfloat z, GLfloat w)
    cdef void glRasterPos4i(GLint x, GLint y, GLint z, GLint w)
    cdef void glRasterPos4s(GLshort x, GLshort y, GLshort z, GLshort w)
    cdef void glRasterPos2dv(GLdouble *v)
    cdef void glRasterPos2fv(GLfloat *v)
    cdef void glRasterPos2iv(GLint *v)
    cdef void glRasterPos2sv(GLshort *v)
    cdef void glRasterPos3dv(GLdouble *v)
    cdef void glRasterPos3fv(GLfloat *v)
    cdef void glRasterPos3iv(GLint *v)
    cdef void glRasterPos3sv(GLshort *v)
    cdef void glRasterPos4dv(GLdouble *v)
    cdef void glRasterPos4fv(GLfloat *v)
    cdef void glRasterPos4iv(GLint *v)
    cdef void glRasterPos4sv(GLshort *v)
    cdef void glRectd(GLdouble x1, GLdouble y1, GLdouble x2, GLdouble y2)
    cdef void glRectf(GLfloat x1, GLfloat y1, GLfloat x2, GLfloat y2)
    cdef void glRecti(GLint x1, GLint y1, GLint x2, GLint y2)
    cdef void glRects(GLshort x1, GLshort y1, GLshort x2, GLshort y2)
    cdef void glRectdv(GLdouble *v1, GLdouble *v2)
    cdef void glRectfv(GLfloat *v1, GLfloat *v2)
    cdef void glRectiv(GLint *v1, GLint *v2)
    cdef void glRectsv(GLshort *v1, GLshort *v2)
    cdef void glVertexPointer(GLint size, GLenum type, GLsizei stride, GLvoid *ptr)
    cdef void glNormalPointer(GLenum type, GLsizei stride, GLvoid *ptr)
    cdef void glColorPointer(GLint size, GLenum type, GLsizei stride, GLvoid *ptr)
    cdef void glIndexPointer(GLenum type, GLsizei stride, GLvoid *ptr)
    cdef void glTexCoordPointer(GLint size, GLenum type, GLsizei stride, GLvoid *ptr)
    cdef void glEdgeFlagPointer(GLsizei stride, GLvoid *ptr)
    cdef void glGetPointerv(GLenum pname, GLvoid **params)
    cdef void glArrayElement(GLint i)
    cdef void glDrawArrays(GLenum mode, GLint first, GLsizei count)
    cdef void glDrawElements(GLenum mode, GLsizei count, GLenum type, GLvoid *indices)
    cdef void glInterleavedArrays(GLenum format, GLsizei stride, GLvoid *pointer)
    cdef void glShadeModel(GLenum mode)
    cdef void glLightf(GLenum light, GLenum pname, GLfloat param)
    cdef void glLighti(GLenum light, GLenum pname, GLint param)
    cdef void glLightfv(GLenum light, GLenum pname, GLfloat *params)
    cdef void glLightiv(GLenum light, GLenum pname, GLint *params)
    cdef void glGetLightfv(GLenum light, GLenum pname, GLfloat *params)
    cdef void glGetLightiv(GLenum light, GLenum pname, GLint *params)
    cdef void glLightModelf(GLenum pname, GLfloat param)
    cdef void glLightModeli(GLenum pname, GLint param)
    cdef void glLightModelfv(GLenum pname, GLfloat *params)
    cdef void glLightModeliv(GLenum pname, GLint *params)
    cdef void glMaterialf(GLenum face, GLenum pname, GLfloat param)
    cdef void glMateriali(GLenum face, GLenum pname, GLint param)
    cdef void glMaterialfv(GLenum face, GLenum pname, GLfloat *params)
    cdef void glMaterialiv(GLenum face, GLenum pname, GLint *params)
    cdef void glGetMaterialfv(GLenum face, GLenum pname, GLfloat *params)
    cdef void glGetMaterialiv(GLenum face, GLenum pname, GLint *params)
    cdef void glColorMaterial(GLenum face, GLenum mode)
    cdef void glPixelZoom(GLfloat xfactor, GLfloat yfactor)
    cdef void glPixelStoref(GLenum pname, GLfloat param)
    cdef void glPixelStorei(GLenum pname, GLint param)
    cdef void glPixelTransferf(GLenum pname, GLfloat param)
    cdef void glPixelTransferi(GLenum pname, GLint param)
    cdef void glPixelMapfv(GLenum map, GLint mapsize, GLfloat *values)
    cdef void glPixelMapuiv(GLenum map, GLint mapsize, GLuint *values)
    cdef void glPixelMapusv(GLenum map, GLint mapsize, GLushort *values)
    cdef void glGetPixelMapfv(GLenum map, GLfloat *values)
    cdef void glGetPixelMapuiv(GLenum map, GLuint *values)
    cdef void glGetPixelMapusv(GLenum map, GLushort *values)
    cdef void glBitmap(GLsizei width, GLsizei height, GLfloat xorig, GLfloat yorig, GLfloat xmove, GLfloat ymove, GLubyte *bitmap)
    cdef void glReadPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glDrawPixels(GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glCopyPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum type)
    cdef void glStencilFunc(GLenum func, GLint ref, GLuint mask)
    cdef void glStencilMask(GLuint mask)
    cdef void glStencilOp(GLenum fail, GLenum zfail, GLenum zpass)
    cdef void glClearStencil(GLint s)
    cdef void glTexGend(GLenum coord, GLenum pname, GLdouble param)
    cdef void glTexGenf(GLenum coord, GLenum pname, GLfloat param)
    cdef void glTexGeni(GLenum coord, GLenum pname, GLint param)
    cdef void glTexGendv(GLenum coord, GLenum pname, GLdouble *params)
    cdef void glTexGenfv(GLenum coord, GLenum pname, GLfloat *params)
    cdef void glTexGeniv(GLenum coord, GLenum pname, GLint *params)
    cdef void glGetTexGendv(GLenum coord, GLenum pname, GLdouble *params)
    cdef void glGetTexGenfv(GLenum coord, GLenum pname, GLfloat *params)
    cdef void glGetTexGeniv(GLenum coord, GLenum pname, GLint *params)
    cdef void glTexEnvf(GLenum target, GLenum pname, GLfloat param)
    cdef void glTexEnvi(GLenum target, GLenum pname, GLint param)
    cdef void glTexEnvfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glTexEnviv(GLenum target, GLenum pname, GLint *params)
    cdef void glGetTexEnvfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glGetTexEnviv(GLenum target, GLenum pname, GLint *params)
    cdef void glTexParameterf(GLenum target, GLenum pname, GLfloat param)
    cdef void glTexParameteri(GLenum target, GLenum pname, GLint param)
    cdef void glTexParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glTexParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glGetTexParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glGetTexParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glGetTexLevelParameterfv(GLenum target, GLint level, GLenum pname, GLfloat *params)
    cdef void glGetTexLevelParameteriv(GLenum target, GLint level, GLenum pname, GLint *params)
    cdef void glTexImage1D(GLenum target, GLint level, GLint internalFormat, GLsizei width, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glTexImage2D(GLenum target, GLint level, GLint internalFormat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glGetTexImage(GLenum target, GLint level, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glGenTextures(GLsizei n, GLuint *textures)
    cdef void glDeleteTextures(GLsizei n, GLuint *textures)
    cdef void glBindTexture(GLenum target, GLuint texture)
    cdef void glPrioritizeTextures(GLsizei n, GLuint *textures, GLclampf *priorities)
    cdef GLboolean glAreTexturesResident(GLsizei n, GLuint *textures, GLboolean *residences)
    cdef GLboolean glIsTexture(GLuint texture)
    cdef void glTexSubImage1D(GLenum target, GLint level, GLint xoffset, GLsizei width, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glCopyTexImage1D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLint border)
    cdef void glCopyTexImage2D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border)
    cdef void glCopyTexSubImage1D(GLenum target, GLint level, GLint xoffset, GLint x, GLint y, GLsizei width)
    cdef void glCopyTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glMap1d(GLenum target, GLdouble u1, GLdouble u2, GLint stride, GLint order, GLdouble *points)
    cdef void glMap1f(GLenum target, GLfloat u1, GLfloat u2, GLint stride, GLint order, GLfloat *points)
    cdef void glMap2d(GLenum target, GLdouble u1, GLdouble u2, GLint ustride, GLint uorder, GLdouble v1, GLdouble v2, GLint vstride, GLint vorder, GLdouble *points)
    cdef void glMap2f(GLenum target, GLfloat u1, GLfloat u2, GLint ustride, GLint uorder, GLfloat v1, GLfloat v2, GLint vstride, GLint vorder, GLfloat *points)
    cdef void glGetMapdv(GLenum target, GLenum query, GLdouble *v)
    cdef void glGetMapfv(GLenum target, GLenum query, GLfloat *v)
    cdef void glGetMapiv(GLenum target, GLenum query, GLint *v)
    cdef void glEvalCoord1d(GLdouble u)
    cdef void glEvalCoord1f(GLfloat u)
    cdef void glEvalCoord1dv(GLdouble *u)
    cdef void glEvalCoord1fv(GLfloat *u)
    cdef void glEvalCoord2d(GLdouble u, GLdouble v)
    cdef void glEvalCoord2f(GLfloat u, GLfloat v)
    cdef void glEvalCoord2dv(GLdouble *u)
    cdef void glEvalCoord2fv(GLfloat *u)
    cdef void glMapGrid1d(GLint un, GLdouble u1, GLdouble u2)
    cdef void glMapGrid1f(GLint un, GLfloat u1, GLfloat u2)
    cdef void glMapGrid2d(GLint un, GLdouble u1, GLdouble u2, GLint vn, GLdouble v1, GLdouble v2)
    cdef void glMapGrid2f(GLint un, GLfloat u1, GLfloat u2, GLint vn, GLfloat v1, GLfloat v2)
    cdef void glEvalPoint1(GLint i)
    cdef void glEvalPoint2(GLint i, GLint j)
    cdef void glEvalMesh1(GLenum mode, GLint i1, GLint i2)
    cdef void glEvalMesh2(GLenum mode, GLint i1, GLint i2, GLint j1, GLint j2)
    cdef void glFogf(GLenum pname, GLfloat param)
    cdef void glFogi(GLenum pname, GLint param)
    cdef void glFogfv(GLenum pname, GLfloat *params)
    cdef void glFogiv(GLenum pname, GLint *params)
    cdef void glFeedbackBuffer(GLsizei size, GLenum type, GLfloat *buffer)
    cdef void glPassThrough(GLfloat token)
    cdef void glSelectBuffer(GLsizei size, GLuint *buffer)
    cdef void glInitNames()
    cdef void glLoadName(GLuint name)
    cdef void glPushName(GLuint name)
    cdef void glPopName()
    cdef void glDrawRangeElements(GLenum mode, GLuint start, GLuint end, GLsizei count, GLenum type, GLvoid *indices)
    cdef void glTexImage3D(GLenum target, GLint level, GLenum internalFormat, GLsizei width, GLsizei height, GLsizei depth, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glTexSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset, GLsizei width, GLsizei height, GLsizei depth, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glCopyTexSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset, GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glColorTable(GLenum target, GLenum internalformat, GLsizei width, GLenum format, GLenum type, GLvoid *table)
    cdef void glColorSubTable(GLenum target, GLsizei start, GLsizei count, GLenum format, GLenum type, GLvoid *data)
    cdef void glColorTableParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glColorTableParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glCopyColorSubTable(GLenum target, GLsizei start, GLint x, GLint y, GLsizei width)
    cdef void glCopyColorTable(GLenum target, GLenum internalformat, GLint x, GLint y, GLsizei width)
    cdef void glGetColorTable(GLenum target, GLenum format, GLenum type, GLvoid *table)
    cdef void glGetColorTableParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glGetColorTableParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glBlendEquation(GLenum mode)
    cdef void glBlendColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
    cdef void glHistogram(GLenum target, GLsizei width, GLenum internalformat, GLboolean sink)
    cdef void glResetHistogram(GLenum target)
    cdef void glGetHistogram(GLenum target, GLboolean reset, GLenum format, GLenum type, GLvoid *values)
    cdef void glGetHistogramParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glGetHistogramParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glMinmax(GLenum target, GLenum internalformat, GLboolean sink)
    cdef void glResetMinmax(GLenum target)
    cdef void glGetMinmax(GLenum target, GLboolean reset, GLenum format, GLenum types, GLvoid *values)
    cdef void glGetMinmaxParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glGetMinmaxParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glConvolutionFilter1D(GLenum target, GLenum internalformat, GLsizei width, GLenum format, GLenum type, GLvoid *image)
    cdef void glConvolutionFilter2D(GLenum target, GLenum internalformat, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *image)
    cdef void glConvolutionParameterf(GLenum target, GLenum pname, GLfloat params)
    cdef void glConvolutionParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glConvolutionParameteri(GLenum target, GLenum pname, GLint params)
    cdef void glConvolutionParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glCopyConvolutionFilter1D(GLenum target, GLenum internalformat, GLint x, GLint y, GLsizei width)
    cdef void glCopyConvolutionFilter2D(GLenum target, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glGetConvolutionFilter(GLenum target, GLenum format, GLenum type, GLvoid *image)
    cdef void glGetConvolutionParameterfv(GLenum target, GLenum pname, GLfloat *params)
    cdef void glGetConvolutionParameteriv(GLenum target, GLenum pname, GLint *params)
    cdef void glSeparableFilter2D(GLenum target, GLenum internalformat, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *row, GLvoid *column)
    cdef void glGetSeparableFilter(GLenum target, GLenum format, GLenum type, GLvoid *row, GLvoid *column, GLvoid *span)
    cdef void glActiveTextureARB(GLenum texture)
    cdef void glClientActiveTexture(GLenum texture)
    cdef void glCompressedTexImage1D(GLenum target, GLint level, GLenum internalformat, GLsizei width, GLint border, GLsizei imageSize, GLvoid *data)
    cdef void glCompressedTexImage2D(GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLint border, GLsizei imageSize, GLvoid *data)
    cdef void glCompressedTexImage3D(GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLsizei depth, GLint border, GLsizei imageSize, GLvoid *data)
    cdef void glCompressedTexSubImage1D(GLenum target, GLint level, GLint xoffset, GLsizei width, GLenum format, GLsizei imageSize, GLvoid *data)
    cdef void glCompressedTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLsizei imageSize, GLvoid *data)
    cdef void glCompressedTexSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset, GLsizei width, GLsizei height, GLsizei depth, GLenum format, GLsizei imageSize, GLvoid *data)
    cdef void glGetCompressedTexImage(GLenum target, GLint lod, GLvoid *img)
    cdef void glMultiTexCoord1dARB(GLenum target, GLdouble s)
    cdef void glMultiTexCoord1dvARB(GLenum target, GLdouble *v)
    cdef void glMultiTexCoord1fARB(GLenum target, GLfloat s)
    cdef void glMultiTexCoord1fvARB(GLenum target, GLfloat *v)
    cdef void glMultiTexCoord1iARB(GLenum target, GLint s)
    cdef void glMultiTexCoord1ivARB(GLenum target, GLint *v)
    cdef void glMultiTexCoord1sARB(GLenum target, GLshort s)
    cdef void glMultiTexCoord1svARB(GLenum target, GLshort *v)
    cdef void glMultiTexCoord2dARB(GLenum target, GLdouble s, GLdouble t)
    cdef void glMultiTexCoord2dvARB(GLenum target, GLdouble *v)
    cdef void glMultiTexCoord2fARB(GLenum target, GLfloat s, GLfloat t)
    cdef void glMultiTexCoord2fvARB(GLenum target, GLfloat *v)
    cdef void glMultiTexCoord2iARB(GLenum target, GLint s, GLint t)
    cdef void glMultiTexCoord2ivARB(GLenum target, GLint *v)
    cdef void glMultiTexCoord2sARB(GLenum target, GLshort s, GLshort t)
    cdef void glMultiTexCoord2svARB(GLenum target, GLshort *v)
    cdef void glMultiTexCoord3dARB(GLenum target, GLdouble s, GLdouble t, GLdouble r)
    cdef void glMultiTexCoord3dvARB(GLenum target, GLdouble *v)
    cdef void glMultiTexCoord3fARB(GLenum target, GLfloat s, GLfloat t, GLfloat r)
    cdef void glMultiTexCoord3fvARB(GLenum target, GLfloat *v)
    cdef void glMultiTexCoord3iARB(GLenum target, GLint s, GLint t, GLint r)
    cdef void glMultiTexCoord3ivARB(GLenum target, GLint *v)
    cdef void glMultiTexCoord3sARB(GLenum target, GLshort s, GLshort t, GLshort r)
    cdef void glMultiTexCoord3svARB(GLenum target, GLshort *v)
    cdef void glMultiTexCoord4dARB(GLenum target, GLdouble s, GLdouble t, GLdouble r, GLdouble q)
    cdef void glMultiTexCoord4dvARB(GLenum target, GLdouble *v)
    cdef void glMultiTexCoord4fARB(GLenum target, GLfloat s, GLfloat t, GLfloat r, GLfloat q)
    cdef void glMultiTexCoord4fvARB(GLenum target, GLfloat *v)
    cdef void glMultiTexCoord4iARB(GLenum target, GLint s, GLint t, GLint r, GLint q)
    cdef void glMultiTexCoord4ivARB(GLenum target, GLint *v)
    cdef void glMultiTexCoord4sARB(GLenum target, GLshort s, GLshort t, GLshort r, GLshort q)
    cdef void glMultiTexCoord4svARB(GLenum target, GLshort *v)
    cdef void glLoadTransposeMatrixd(GLdouble m[16])
    cdef void glLoadTransposeMatrixf(GLfloat m[16])
    cdef void glMultTransposeMatrixd(GLdouble m[16])
    cdef void glMultTransposeMatrixf(GLfloat m[16])
    cdef void glSampleCoverage(GLclampf value, GLboolean invert)

    # Shaders

    int GL_PROGRAM_OBJECT_ARB
    int GL_SHADER_OBJECT_ARB
    int GL_OBJECT_TYPE_ARB
    int GL_OBJECT_SUBTYPE_ARB
    int GL_FLOAT_VEC2_ARB
    int GL_FLOAT_VEC3_ARB
    int GL_FLOAT_VEC4_ARB
    int GL_INT_VEC2_ARB
    int GL_INT_VEC3_ARB
    int GL_INT_VEC4_ARB
    int GL_BOOL_ARB
    int GL_BOOL_VEC2_ARB
    int GL_BOOL_VEC3_ARB
    int GL_BOOL_VEC4_ARB
    int GL_FLOAT_MAT2_ARB
    int GL_FLOAT_MAT3_ARB
    int GL_FLOAT_MAT4_ARB
    int GL_SAMPLER_1D_ARB
    int GL_SAMPLER_2D_ARB
    int GL_SAMPLER_3D_ARB
    int GL_SAMPLER_CUBE_ARB
    int GL_SAMPLER_1D_SHADOW_ARB
    int GL_SAMPLER_2D_SHADOW_ARB
    int GL_SAMPLER_2D_RECT_ARB
    int GL_SAMPLER_2D_RECT_SHADOW_ARB
    int GL_OBJECT_DELETE_STATUS_ARB
    int GL_OBJECT_COMPILE_STATUS_ARB
    int GL_OBJECT_LINK_STATUS_ARB
    int GL_OBJECT_VALIDATE_STATUS_ARB
    int GL_OBJECT_INFO_LOG_LENGTH_ARB
    int GL_OBJECT_ATTACHED_OBJECTS_ARB
    int GL_OBJECT_ACTIVE_UNIFORMS_ARB
    int GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH_ARB
    int GL_OBJECT_SHADER_SOURCE_LENGTH_ARB
    int GL_VERTEX_SHADER_ARB
    int GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB
    int GL_MAX_VARYING_FLOATS_ARB
    int GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS_ARB
    int GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_ARB
    int GL_OBJECT_ACTIVE_ATTRIBUTES_ARB
    int GL_OBJECT_ACTIVE_ATTRIBUTE_MAX_LENGTH_ARB
    int GL_FRAGMENT_PROGRAM_ARB
    int GL_PROGRAM_ALU_INSTRUCTIONS_ARB
    int GL_PROGRAM_TEX_INSTRUCTIONS_ARB
    int GL_PROGRAM_TEX_INDIRECTIONS_ARB
    int GL_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB
    int GL_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB
    int GL_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB
    int GL_MAX_PROGRAM_ALU_INSTRUCTIONS_ARB
    int GL_MAX_PROGRAM_TEX_INSTRUCTIONS_ARB
    int GL_MAX_PROGRAM_TEX_INDIRECTIONS_ARB
    int GL_MAX_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB
    int GL_MAX_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB
    int GL_MAX_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB
    int GL_MAX_TEXTURE_COORDS_ARB
    int GL_MAX_TEXTURE_IMAGE_UNITS_ARB
    int GL_VERTEX_ARRAY
    int GL_NORMAL_ARRAY
    int GL_COLOR_ARRAY
    int GL_INDEX_ARRAY
    int GL_TEXTURE_COORD_ARRAY
    int GL_EDGE_FLAG_ARRAY
    # BeginMode
    int GL_POINTS
    int GL_LINES
    int GL_LINE_LOOP
    int GL_LINE_STRIP
    int GL_TRIANGLES
    int GL_TRIANGLE_STRIP
    int GL_TRIANGLE_FAN
    int GL_QUADS
    int GL_QUAD_STRIP
    int GL_POLYGON
    # BlendingFactorDest
    int GL_ZERO
    int GL_ONE
    int GL_SRC_COLOR
    int GL_ONE_MINUS_SRC_COLOR
    int GL_SRC_ALPHA
    int GL_ONE_MINUS_SRC_ALPHA
    int GL_DST_ALPHA
    int GL_ONE_MINUS_DST_ALPHA
    int GL_BLEND_DST
    int GL_BLEND_SRC
    int GL_BLEND
    # DataType
    int GL_BYTE
    int GL_UNSIGNED_BYTE
    int GL_SHORT
    int GL_UNSIGNED_SHORT
    int GL_INT
    int GL_UNSIGNED_INT
    int GL_FLOAT
    # Boolean
    int GL_FALSE
    int GL_TRUE

    cdef void glGetObjectParameterivARB(GLhandleARB object, GLenum pname, GLint *params)
    cdef void glGetInfoLogARB(GLhandleARB object, GLsizei maxLength, GLsizei *length, GLchar *infoLog)
    cdef void glShaderSourceARB(GLhandleARB shader, GLsizei nstrings, GLchar** strings, GLint *lengths)
    cdef void glCompileShaderARB(GLhandleARB shader)
    cdef GLhandleARB glCreateShaderObjectARB(GLenum shaderType)
    cdef void glAttachObjectARB(GLhandleARB program, GLhandleARB shader)
    cdef void glDetachObjectARB(GLhandleARB program, GLhandleARB shader)
    cdef void glLinkProgramARB(GLhandleARB program)
    cdef void glDeleteObjectARB(GLhandleARB object)

    cdef void glVertexPointer (GLint size, GLenum type, GLsizei stride, GLvoid *pointer)
