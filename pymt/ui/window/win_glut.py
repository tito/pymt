'''
Window GLUT: windowing provider based on GLUT
'''

__all__ = ('MTWindowGlut', )

import sys
import os
from pymt.ui.window import BaseWindow
from pymt.logger import pymt_logger
from pymt.base import stopTouchApp, getEventLoop
from OpenGL.GLUT import GLUT_RGBA, GLUT_DOUBLE, GLUT_ALPHA, GLUT_DEPTH, \
        GLUT_MULTISAMPLE, GLUT_STENCIL, GLUT_ACCUM, GLUT_RIGHT_BUTTON, \
        GLUT_DOWN, GLUT_ACTIVE_CTRL, GLUT_ACTIVE_ALT, GLUT_ACTIVE_SHIFT, \
        glutInitDisplayMode, glutInit, glutCreateWindow, glutReshapeWindow, \
        glutMouseFunc, glutMouseFunc, glutKeyboardFunc, glutShowWindow, \
        glutFullScreen, glutDestroyWindow, glutReshapeFunc, glutDisplayFunc, \
        glutMotionFunc, glutGetModifiers, glutSwapBuffers, glutPostRedisplay, \
        glutMainLoop

class MTWindowGlut(BaseWindow):

    __glut_window = None

    def create_window(self, params):
        if self.__glut_window is None:
            # init GLUT !
            pymt_logger.debug('WinGlut: GLUT initialization')
            glutInit('')
            if 'PYMT_GLUT_UNITTEST' in os.environ:
                glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
            else:
                glutInitDisplayMode(
                    GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH |
                    GLUT_MULTISAMPLE | GLUT_STENCIL | GLUT_ACCUM)

            # create the window
            self.__glut_window = glutCreateWindow('pymt')

        # register all callbcaks
        glutReshapeFunc(self._glut_reshape)
        glutMouseFunc(self._glut_mouse)
        glutMotionFunc(self._glut_mouse_motion)
        glutKeyboardFunc(self._glut_keyboard)

        # update window size
        glutShowWindow()
        self.size = params['width'], params['height']
        if params['fullscreen']:
            pymt_logger.debug('WinGlut: Set window to fullscreen mode')
            glutFullScreen()

        super(MTWindowGlut, self).create_window(params)

    def close(self):
        if self.__glut_window:
            glutDestroyWindow(self.__glut_window)
            self.__glut_window = None
        super(MTWindowGlut, self).close()

    def on_keyboard(self, key, scancode=None, unicode=None):
        self._glut_update_modifiers()
        if ord(key) == 27:
            stopTouchApp()
            return True
        super(MTWindowGlut, self).on_keyboard(key, scancode, unicode)

    def _set_size(self, size):
        if super(MTWindowGlut, self)._set_size(size):
            glutReshapeWindow(*size)
            return True
    size = property(BaseWindow._get_size, _set_size)

    def flip(self):
        glutSwapBuffers()
        super(MTWindowGlut, self).flip()

    def mainloop(self):
        '''Main loop is done by GLUT itself.'''

        # callback for ticking
        def _glut_redisplay():
            evloop = getEventLoop()

            # hack, glut seem can't handle the leaving on the mainloop
            # so... leave with sys.exit() :[
            try:
                evloop.idle()
            except KeyboardInterrupt:
                evloop.quit = True
            if evloop.quit:
                sys.exit(0)

            glutPostRedisplay()

        # install handler
        glutDisplayFunc(_glut_redisplay)

        # run main loop
        glutMainLoop()


    #
    # GLUT callbacks
    #

    def _glut_reshape(self, w, h):
        self.size = w, h

    def _glut_mouse(self, button, state, x, y):
        self._glut_update_modifiers()

        btn = 'left'
        if button == GLUT_RIGHT_BUTTON:
            btn = 'right'

        if state == GLUT_DOWN:
            self.dispatch_event('on_mouse_down', x, y, btn, self.modifiers)
        else:
            self.dispatch_event('on_mouse_up', x, y, btn, self.modifiers)

    def _glut_mouse_motion(self, x, y):
        self.dispatch_event('on_mouse_move', x, y, self.modifiers)

    def _glut_keyboard(self, key, x, y):
        self.dispatch_event('on_keyboard', key, None, None)

    def _glut_update_modifiers(self):
        self._modifiers = []
        mods = glutGetModifiers()
        if mods & GLUT_ACTIVE_SHIFT:
            self._modifiers.append('shift')
        if mods & GLUT_ACTIVE_ALT:
            self._modifiers.append('alt')
        if mods & GLUT_ACTIVE_CTRL:
            self._modifiers.append('ctrl')

