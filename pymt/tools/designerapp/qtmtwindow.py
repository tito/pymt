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
        self.is_running = False
        self.want_leave = False
        self.is_paused = False

    def timerEvent(self, event):
        self.update()

    def minimumSizeHint(self):
        return QtCore.QSize(640, 50)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def paintGL(self):
        pymt_evloop = getEventLoop()
        if pymt_evloop and self.pymt_window:
            # leaving asked ?
            if self.want_leave:
                self.close_pymt_window()
                return

            # do idle only if it's not in paused
            if not self.is_paused:
                pymt_evloop.idle()
        else:
            # force bit to running = False,
            # application can leave by itself
            self.want_leave = False
            self.is_running = False
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

    def reset(self):
        self.resizeGL(self.width(), self.height())
        self.is_running = True
        self.is_paused = False
        self.want_leave = False

    def play(self):
        self.is_paused = False

    def stop(self):
        self.want_leave = True
        self.is_running = False

    def pause(self):
        self.is_paused = True

    def close_pymt_window(self):
        if self.pymt_window:
            self.pymt_window.close()
            self.pymt_window = None

    def create_new_pymt_window(self):
        self.close_pymt_window()
        self.pymt_window = MTDesignerWindow()
        self.reset()

