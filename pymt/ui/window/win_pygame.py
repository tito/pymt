'''
Window Pygame: windowing provider based on Pygame
'''

__all__ = ('MTWindowPygame', )

import os
import pymt
from pymt.ui.window import BaseWindow
from pymt.exceptions import pymt_exception_manager, ExceptionManager
from pymt.logger import pymt_logger
from pymt.base import stopTouchApp, getEventLoop
from OpenGL.GL import glEnable
from OpenGL.GL.ARB.multisample import GL_MULTISAMPLE_ARB

try:
    import pygame
except:
    pymt_logger.warning('WinPygame: Pygame is not installed !')
    raise

class MTWindowPygame(BaseWindow):
    def create_window(self, params):
        # force display to show (available only for fullscreen)
        displayidx = pymt.pymt_config.getint('graphics', 'display')
        if not 'SDL_VIDEO_FULLSCREEN_HEAD' in os.environ and displayidx != -1:
            os.environ['SDL_VIDEO_FULLSCREEN_HEAD'] = '%d' % displayidx

        # init some opengl, same as before.
        self.flags = pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF

        pygame.display.init()

        multisamples = pymt.pymt_config.getint('graphics', 'multisamples')

        if multisamples > 0:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, multisamples)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 16)
        pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 1)
        pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)
        pygame.display.set_caption('pymt')

        self._fullscreenmode = params['fullscreen']
        if self._fullscreenmode == 'fake':
            pymt_logger.debug('WinPygame: Set window to fake fullscreen mode')
            self.flags |= pygame.NOFRAME
            os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

        elif self._fullscreenmode:
            pymt_logger.debug('WinPygame: Set window to fullscreen mode')
            self.flags |= pygame.FULLSCREEN

        #set window icon before calling set_mode
        icon = pygame.image.load(pymt.pymt_config.get('graphics', 'window_icon'))
        pygame.display.set_icon(icon)


        # init ourself size + setmode
        # before calling on_resize
        self._size = params['width'], params['height']
        self._vsync = params['vsync']

        # try to use mode with multisamples
        try:
            self._pygame_set_mode()
        except pygame.error:
            if multisamples:
                pymt_logger.warning('WinPygame: Video: failed (multisamples=%d)' %
                                    multisamples)
                pymt_logger.warning('Video: trying without antialiasing')
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
                multisamples = 0
                self._pygame_set_mode()
            else:
                pymt_logger.warning('WinPygame: Video setup failed :-(')
                raise

        if multisamples:
            try:
                glEnable(GL_MULTISAMPLE_ARB)
            except Exception:
                pass

        super(MTWindowPygame, self).create_window(params)

        # set mouse visibility
        pygame.mouse.set_visible(
            pymt.pymt_config.getboolean('graphics', 'show_cursor'))

    def close(self):
        pygame.display.quit()

    def on_keyboard(self, key, scancode=None, unicode=None):
        if key == 27:
            stopTouchApp()
            self.close()  #not sure what to do here
            return True
        super(MTWindowPygame, self).on_keyboard(key, scancode, unicode)

    def flip(self):
        pygame.display.flip()
        super(MTWindowPygame, self).flip()

        # do software vsync if asked
        # FIXME: vsync is surely not 60 for everyone
        # this is not a real vsync. this must be done by driver...
        # but pygame can't do vsync on X11, and some people
        # use hack to make it work under darwin...
        if self._vsync:
            from pymt.clock import getClock
            import time
            s = 1/60. - (time.time() - getClock().get_time())
            if s > 0:
                time.sleep(s)

    def toggle_fullscreen(self):
        if self.flags & pygame.FULLSCREEN:
            self.flags &= ~pygame.FULLSCREEN
        else:
            self.flags |= pygame.FULLSCREEN
        self._pygame_set_mode()

    def _mainloop(self):
        evloop = getEventLoop()
        evloop.idle()

        for event in pygame.event.get():

            # kill application (SIG_TERM)
            if event.type == pygame.QUIT:
                evloop.quit = True
                self.close()

            # mouse move
            elif event.type == pygame.MOUSEMOTION:
                # don't dispatch motion if no button are pressed
                if event.buttons == (0, 0, 0):
                    continue
                x, y = event.pos
                self.dispatch_event('on_mouse_move', x, y, self.modifiers)

            # mouse action
            elif event.type in (pygame.MOUSEBUTTONDOWN,
                                pygame.MOUSEBUTTONUP):
                self._pygame_update_modifiers()
                x, y = event.pos
                btn = 'left'
                if event.button == 3:
                    btn = 'right'
                elif event.button == 2:
                    btn = 'middle'
                eventname = 'on_mouse_down'
                if event.type == pygame.MOUSEBUTTONUP:
                    eventname = 'on_mouse_up'
                self.dispatch_event(eventname, x, y, btn, self.modifiers)

            # keyboard action
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self._pygame_update_modifiers(event.mod)
                # atm, don't handle keyup
                if event.type == pygame.KEYUP:
                    self.dispatch_event('on_key_up', event.key,
                        event.scancode)
                    continue

                # don't dispatch more key if down event is accepted
                if self.dispatch_event('on_key_down', event.key,
                                       event.scancode, event.unicode):
                    continue
                self.dispatch_event('on_keyboard', event.key,
                                    event.scancode, event.unicode)

            # video resize
            elif event.type == pygame.VIDEORESIZE:
                pass

            # ignored event
            elif event.type in (pygame.ACTIVEEVENT, pygame.VIDEOEXPOSE):
                pass

            # unhandled event !
            else:
                pymt_logger.debug('WinPygame: Unhandled event %s' % str(event))

    def mainloop(self):
        # don't known why, but pygame required a resize event
        # for opengl, before mainloop... window reinit ?
        self.dispatch_event('on_resize', *self.size)

        evloop = getEventLoop()
        while not evloop.quit:
            try:
                self._mainloop()
                if not pygame.display.get_active():
                    pygame.time.wait(100)
            except BaseException, inst:
                # use exception manager first
                r = pymt_exception_manager.handle_exception(inst)
                if r == ExceptionManager.RAISE:
                    stopTouchApp()
                    raise
                else:
                    pass

        # force deletion of window
        pygame.display.quit()


    def _set_size(self, size):
        if super(MTWindowPygame, self)._set_size(size):
            self._pygame_set_mode()
            return True
    size = property(BaseWindow._get_size, _set_size)


    #
    # Pygame wrapper
    #
    def _pygame_set_mode(self, size=None):
        if size is None:
            size = self.size
        if self._fullscreenmode == 'auto':
            pygame.display.set_mode((0, 0), self.flags)
            info = pygame.display.Info()
            self._size = (info.current_w, info.current_h)
        else:
            pygame.display.set_mode(size, self.flags)

    def _pygame_update_modifiers(self, mods=None):
        # Available mod, from dir(pygame)
        # 'KMOD_ALT', 'KMOD_CAPS', 'KMOD_CTRL', 'KMOD_LALT',
        # 'KMOD_LCTRL', 'KMOD_LMETA', 'KMOD_LSHIFT', 'KMOD_META',
        # 'KMOD_MODE', 'KMOD_NONE'
        if mods is None:
            mods = pygame.key.get_mods()
        self._modifiers = []
        if mods & (pygame.KMOD_SHIFT | pygame.KMOD_LSHIFT):
            self._modifiers.append('shift')
        if mods & (pygame.KMOD_ALT | pygame.KMOD_LALT):
            self._modifiers.append('alt')
        if mods & (pygame.KMOD_CTRL | pygame.KMOD_LCTRL):
            self._modifiers.append('ctrl')
