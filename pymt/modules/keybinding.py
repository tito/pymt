'''
Use keyboard to do some action
'''

__all__ = ('start', 'stop')

import logging
from pymt.base import getWindow
from pymt.graphx import drawRectangle, drawLabel, set_color, drawLine, drawCircle
from pymt.logger import pymt_logger_history, pymt_logger

_toggle_state = ''

def toggle(id):
    global _toggle_state
    if _toggle_state == id:
        _toggle_state = ''
    else:
        _toggle_state = id
    if _toggle_state == '':
        return

def _screenshot():
    import os
    import pygame
    from OpenGL.GL import glReadBuffer, glReadPixels, GL_RGB, GL_UNSIGNED_BYTE, GL_FRONT
    win = getWindow()
    glReadBuffer(GL_FRONT)
    data = glReadPixels(0, 0, win.width, win.height, GL_RGB, GL_UNSIGNED_BYTE)
    surface = pygame.image.fromstring(str(buffer(data)), win.size, 'RGB', True)
    filename = None
    for i in xrange(9999):
        path = os.path.join(os.getcwd(), 'screenshot%04d.tga' % i)
        if not os.path.exists(path):
            filename = path
            break
    if filename:
        try:
            pygame.image.save(surface, filename)
            pymt_logger.info('KeyBinding: Screenshot saved at %s' % filename)
        except:
            pymt_logger.exception('KeyBinding: Unable to take a screenshot')
    else:
        pymt_logger.warning('KeyBinding: Unable to take screenshot, no more slot available')

def _on_draw():
    global _toggle_state
    if _toggle_state == '':
        return

    win = getWindow()

    #
    # Show HELP screen
    #
    if _toggle_state == 'help':

        # draw the usual window
        win.on_draw()

        # make background more black
        set_color(0, 0, 0, .8)
        drawRectangle(size=win.size)

        # prepare calculation
        w2 = win.width / 2.
        h2 = win.height / 2.
        k = {'font_size': 24}

        # draw help
        drawLabel('PyMT Keybinding',
                  pos=(w2, win.height - 100), font_size=40)
        drawLabel('Press F1 to leave help',
                  pos=(w2, win.height - 160), font_size=12)
        drawLabel('F1 - Show Help',
                  pos=(w2, h2), **k)
        drawLabel('F2 - Show FPS (%s)' % str(win.show_fps),
                  pos=(w2, h2 - 35), **k)
        drawLabel('F3 - Draw back gradient (%s)' % str(win.gradient),
                  pos=(w2, h2 - 70), **k)
        drawLabel('F4 - Show Calibration screen',
                  pos=(w2, h2 - 105), **k)
        drawLabel('F5 - Toggle fullscreen',
                  pos=(w2, h2 - 140), **k)
        drawLabel('F6 - Show log',
                  pos=(w2, h2 - 175), **k)
        drawLabel('F12 - Screenshot',
                  pos=(w2, h2 - 210), **k)

        return True

    # 
    # Draw calibration screen
    #
    elif _toggle_state == 'calibration':
        step = 8
        ratio = win.height / float(win.width)
        stepx = win.width / step
        stepy = win.height / int(step * ratio)

        # draw black background
        set_color(0, 0, 0)
        drawRectangle(size=win.size)

        # draw lines
        set_color(1, 1, 1)
        for x in xrange(0, win.width, stepx):
            drawLine((x, 0, x, win.height))
        for y in xrange(0, win.height, stepy):
            drawLine((0, y, win.width, y))

        # draw circles
        drawCircle(pos=(win.width / 2., win.height / 2.),
                   radius=win.width / step, linewidth = 2.)
        drawCircle(pos=(win.width / 2., win.height / 2.),
                   radius=(win.width / step) * 2, linewidth = 2.)
        drawCircle(pos=(win.width / 2., win.height / 2.),
                   radius=(win.width / step) * 3, linewidth = 2.)

        return True


    #
    # Draw calibration screen 2 (colors)
    #
    elif _toggle_state == 'calibration2':

        # draw black background
        set_color(0, 0, 0)
        drawRectangle(size=win.size)

        # gray
        step = 25
        stepx = (win.width - 100) / step
        stepy = stepx * 2
        sizew = stepx * step
        sizeh = stepy * step
        w2 = win.width / 2.
        h2 = win.height / 2.
        for _x in xrange(step):
            x = w2 - sizew / 2. + _x * stepx
            drawLabel(chr(65+_x), pos=(x + stepx / 2., h2 + 190))
            c = _x / float(step)

            # grey
            set_color(c, c, c)
            drawRectangle(pos=(x, h2 + 100), size=(stepx, stepy))

            # red
            set_color(c, 0, 0)
            drawRectangle(pos=(x, h2 + 80 - stepy), size=(stepx, stepy))

            # green
            set_color(0, c, 0)
            drawRectangle(pos=(x, h2 + 60 - stepy * 2), size=(stepx, stepy))

            # blue
            set_color(0, 0, c)
            drawRectangle(pos=(x, h2 + 40 - stepy * 3), size=(stepx, stepy))
        return True


    #
    # Draw log screen
    #
    elif _toggle_state == 'log':

        # draw the usual window
        win.on_draw()

        # make background more black
        set_color(0, 0, 0, .8)
        drawRectangle(size=win.size)


        # calculation
        w2 = win.width / 2.
        h2 = win.height / 2.
        k = {'font_size': 11, 'center': False}
        y = win.height - 20
        y = h2
        max = int((h2 / 20))
        levels = {
            logging.DEBUG:    ('DEBUG', (.4,.4,1)),
            logging.INFO:     ('INFO', (.4,1,.4)),
            logging.WARNING:  ('WARNING', (1,1,.4)),
            logging.ERROR:    ('ERROR', (1,.4,.4)),
            logging.CRITICAL: ('CRITICAL', (1,.4,.4)),
        }

        # draw title
        drawLabel('PyMT logger',
                  pos=(w2, win.height - 100), font_size=40)

        # draw logs
        for log in reversed(pymt_logger_history.history[:max]):
            levelname, color = levels[log.levelno]
            msg = log.message.split('\n')[0]
            x = 10
            s = drawLabel('[', pos=(x, y), **k)
            x += s[0]
            s = drawLabel(levelname, pos=(x, y), color=color, **k)
            x += s[0]
            s = drawLabel(']', pos=(x, y), **k)
            x += s[0]
            drawLabel(msg, pos=(100, y), **k)
            y -= 20
        return True



def _on_keyboard_handler(key, scancode, unicode):
    if key is None:
        return
    win = getWindow()
    if key == 282: # F1
        toggle('help')
    elif key == 283: # F2
        win.show_fps = not win.show_fps
    elif key == 284: # F3
        win.gradient = not win.gradient
    elif key == 285: # F4
        # rotating between calibration screen
        if _toggle_state == 'calibration':
            toggle('calibration2')
        elif _toggle_state == 'calibration2':
            toggle('')
        else:
            toggle('calibration')
    elif key == 286: # F5
        win.toggle_fullscreen()
    elif key == 287: # F6
        toggle('log')
    elif key == 293:
        _screenshot()


def start(win, ctx):
    win.push_handlers(on_keyboard=_on_keyboard_handler)
    win.push_handlers(on_draw=_on_draw)

def stop(win, ctx):
    win.remove_handlers(on_keyboard=_on_keyboard_handler)
    win.remove_handlers(on_draw=_on_draw)
