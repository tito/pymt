import sys
import math
from OpenGL.GL import *
from PyQt4 import QtOpenGL, QtGui, QtCore
from pymt import BaseWindow, getEventLoop


class MTSlaveWindow(BaseWindow):
    pass


class MTWindow(QtOpenGL.QGLWidget):

    def __init__(self, parent=None):
        super(MTWindow, self).__init__(parent)
        self.runing_pymt = False
        self.object = 0
        self.bg_color = QtGui.QColor(.5, .5, .5, 1.0)

    def minimumSizeHint(self):
        return QtCore.QSize(640, 50)

    def sizeHint(self):
        return QtCore.QSize(800, 600)


    def initializeGL(self):
        self.qglClearColor(self.bg_color)

    def paintGL(self):
        pymt_evloop = getEventLoop()
        if pymt_evloop and self.pymt_window:
            pymt_evloop.idle()

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
        pos = event.pos()
        x,y = pos.x, pos.y

        #if event.button == Qt.LeftButton
        #if event.button == Qt.RightButton

    def mouseMoveEvent(self, event):
        pos = event.pos()
        x,y = pos.x, pos.y

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        x,y = pos.x, pos.y




