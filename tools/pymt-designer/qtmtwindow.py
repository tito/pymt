import sys
import math
from OpenGL.GL import *
from PyQt4 import QtOpenGL, QtGui, QtCore
from pymt import BaseWindow, getEventLoop


class MTDesignerWindow(BaseWindow):
    pass

class QTMTWindow(QtOpenGL.QGLWidget):

    def __init__(self, parent=None):
        super(QTMTWindow, self).__init__(parent)
        self.runing_pymt = False
        self.pymt_window = False
        self.object = 0
        self.bg_color = QtGui.QColor(.5, .5, .5, 1.0)
        self.startTimer(40)


    def timerEvent(self, event):
        self.update()

    def minimumSizeHint(self):
        return QtCore.QSize(640, 50)

    def sizeHint(self):
        return QtCore.QSize(800, 600)


    def paintGL(self):
        pymt_evloop = getEventLoop()
        if pymt_evloop and self.pymt_window:
            pymt_evloop.idle()
        else:
            glClearColor(0,1,0,1)
            glClear(GL_COLOR_BUFFER_BIT)

    def resizeGL(self, width, height):
        if self.pymt_window:
            self.pymt_window.size = (width, height)

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

    def create_new_pymt_window(self):
        if self.pymt_window:
            self.pymt_window.close()
            self.pymt_window = None
        self.pymt_window = MTDesignerWindow()
        self.resizeGL(self.width(), self.height())

