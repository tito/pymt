import sys
import math
from OpenGL.GL import *
from PyQt4 import QtOpenGL, QtGui, QtCore
from PyQt4.Qt import Qt
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


    def read_mouse_properties(self, event):
        pos = event.pos()
        x,y = pos.x(), pos.y()
        button = 'left'
        if event.button == Qt.RightButton:
            button = 'right'

        self.modifiers = []
        kmods = event.modifiers()
        if kmods & Qt.ShiftModifier:
            self.modifiers.append('shift')
        if kmods & Qt.ControlModifier:
            self.modifiers.append('ctrl')
        if kmods & Qt.AltModifier:
            self.modifiers.append('alt')
        if kmods & Qt.MetaModifier:
            self.modifiers.append('meta')

        return x, y, button, self.modifiers


    def mousePressEvent(self, event):
        if self.pymt_window:
            x,y,b,m = self.read_mouse_properties(event)
            self.pymt_window.dispatch_event('on_mouse_down', x,y,b,m)


    def mouseMoveEvent(self, event):
        if self.pymt_window:
            x,y,b,m = self.read_mouse_properties(event)
            self.pymt_window.dispatch_event('on_mouse_move', x,y,m)

    def mouseReleaseEvent(self, event):
        if self.pymt_window:
            x,y,b,m = self.read_mouse_properties(event)
            self.pymt_window.dispatch_event('on_mouse_up', x,y,b,m)


    def create_new_pymt_window(self):
        if self.pymt_window:
            self.pymt_window.close()
            self.pymt_window = None
        self.pymt_window = MTDesignerWindow()
        self.resizeGL(self.width(), self.height())

