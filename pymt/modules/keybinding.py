'''
Use keyboard to do some action
'''

__all__ = ('start', 'stop')

from pymt.base import getWindow
from pymt.graphx import drawRectangle, drawLabel, set_color, drawLine, drawCircle

_toggle_state = ''

def toggle(id):
    global _toggle_state
    if _toggle_state == id:
        _toggle_state = ''
    else:
        _toggle_state = id
    if _toggle_state == '':
        return

def _on_draw():
    global _toggle_state
    if _toggle_state == '':
        return

    win = getWindow()
    if _toggle_state == 'help':
        win.on_draw()

        set_color(0, 0, 0, .8)
        drawRectangle(size=win.size)
        w2 = win.width / 2.
        h2 = win.height / 2.
        k = {'font_size': 24}
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

        return True

    elif _toggle_state == 'calibration':
        ratio = win.height / float(win.width)
        step = 8
        stepx = win.width / step
        stepy = win.height / int(step * ratio)

        set_color(0, 0, 0)
        drawRectangle(size=win.size)

        set_color(1, 1, 1)
        for x in xrange(0, win.width, stepx):
            drawLine((x, 0, x, win.height))
        for y in xrange(0, win.height, stepy):
            drawLine((0, y, win.width, y))

        drawCircle(pos=(win.width / 2., win.height / 2.),
                   radius=win.width / step, linewidth = 2.)

        drawCircle(pos=(win.width / 2., win.height / 2.),
                   radius=(win.width / step) * 2, linewidth = 2.)

        drawCircle(pos=(win.width / 2., win.height / 2.),
                   radius=(win.width / step) * 3, linewidth = 2.)

        return True

    elif _toggle_state == 'calibration2':
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


def start(win, ctx):
    win.push_handlers(on_keyboard=_on_keyboard_handler)
    win.push_handlers(on_draw=_on_draw)

def stop(win, ctx):
    win.remove_handlers(on_keyboard=_on_keyboard_handler)
    win.remove_handlers(on_draw=_on_draw)
