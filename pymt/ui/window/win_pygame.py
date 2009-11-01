'''
Window Pygame: windowing provider based on Pygame
'''

__all__ = ('MTWindowPygame', )

from . import BaseWindow
from ...logger import pymt_logger
from ...utils import curry
from ...base import stopTouchApp, getEventLoop

try:
    import pygame
except:
    pymt_logger.warning('Pygame is not installed !')
    raise

class MTWindowPygame(BaseWindow):
    def __init__(self, **kwargs):
        # init some opengl, same as before.
        self.flags = pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF
        pygame.display.init()
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 16)
        pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 1)
        pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)

        super(MTWindowPygame, self).__init__(**kwargs)

    def create_window(self):

        if self.shadow:
            pymt_logger.debug('Set next window as Shadow window (1x1)')
            self.flags |= pygame.RESIZABLE
            self._pygame_set_mode((1, 1))
        else:
            self.flags &= ~pygame.RESIZABLE

        pymt_logger.debug('Create the window (shadow=%s)' % str(self.shadow))
        pygame.display.set_caption('pymt')

        super(MTWindowPygame, self).create_window()

    def configure(self, params):
        if params['fullscreen']:
            pymt_logger.debug('Set window to fullscreen mode')
            self.flags |= pygame.FULLSCREEN
        self.size = params['width'], params['height']

        super(MTWindowPygame, self).configure(params)

    def close(self):
        global glut_window
        if glut_window:
            glutDestroyWindow(glut_window)
            glut_window = None
        super(MTWindowPygame, self).close()

    def on_keyboard(self, key, scancode=None, unicode=None):
        if key == 27:
            stopTouchApp()
            return True
        super(MTWindowPygame, self).on_keyboard(key, scancode, unicode)

    def flip(self):
        pygame.display.flip()
        super(MTWindowPygame, self).flip()

    def mainloop(self):
        evloop = getEventLoop()
        while not evloop.quit:

            evloop.idle()

            for event in pygame.event.get():

                # kill application (SIG_TERM)
                if event.type == pygame.QUIT:
                    evloop.quit = True

                # mouse move
                elif event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    self.dispatch_event('on_mouse_move', x, y, self.modifiers)

                # mouse action
                elif event.type in (pygame.MOUSEBUTTONDOWN,
                                    pygame.MOUSEBUTTONUP):
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
                    pymt_logger.debug('Unhandled event %s' % str(event))

    def _set_size(self, size):
        # set pygame mode only if size have really changed
        if super(MTWindowPygame, self)._set_size(size):
            self._pygame_set_mode()


    #
    # Pygame wrapper
    #
    def _pygame_set_mode(self, size=None):
        if size is None:
            size = self.size
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
