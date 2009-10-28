import sys
import math
from OpenGL.GL import *
from PyQt4 import QtOpenGL, QtGui, QtCore

class MTWindow(QtOpenGL.QGLWidget):

    def __init__(self, parent=None):
        super(MTWindow, self).__init__(parent)

        self.object = 0
        self.bg_color = QtGui.QColor(.5, .5, .5, 1.0)

    def minimumSizeHint(self):
        return QtCore.QSize(640, 50)

    def sizeHint(self):
        return QtCore.QSize(800, 600)


    def initializeGL(self):
        self.qglClearColor(self.bg_color)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        glViewport((width - side) / 2, (height - side) / 2, side, side)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        pass
    def mouseMoveEvent(self, event):
        pass


