# A rewrite of MTVKeyboard with pills.
# Should really speed up.
# Work in progress !

from pymt import *
from pyglet.gl import GL_LINE_LOOP

class KeyboardLayout(object):
    pass

class KeyboardLayoutQWERTY(KeyboardLayout):
    LINE_1 = [
        ('~', '~', None, 1),    ('!', '!', None, 1),    ('@', '@', None, 1),
        ('#', '#', None, 1),    ('$', '$', None, 1),    ('%', '%', None, 1),
        ('^', '^', None, 1),    ('&', '&', None, 1),    ('*', '*', None, 1),
        ('(', '(', None, 1),    (')', ')', None, 1),    ('_', '_', None, 1),
        ('+', '+', None, 1),    ('Backspace', None, 'backspace', 2),
    ]
    LINE_2 = [
        ('Tab', chr(0x09), None, 1.5),  ('q', 'q', None, 1),    ('w', 'w', None, 1),
        ('e', 'e', None, 1),    ('r', 'r', None, 1),    ('t', 't', None, 1),
        ('y', 'y', None, 1),    ('u', 'u', None, 1),    ('i', 'i', None, 1),
        ('o', 'o', None, 1),    ('p', 'p', None, 1),    ('{', '{', None, 1),
        ('}', '}', None, 1),    ('|', '|', None, 1.5)
    ]
    LINE_3 = [
        ('Caps Lock', None, 'capslook', 1.8),  ('a', 'a', None, 1),    ('s', 's', None, 1),
        ('d', 'd', None, 1),    ('f', 'f', None, 1),    ('g', 'g', None, 1),
        ('h', 'h', None, 1),    ('j', 'j', None, 1),    ('k', 'k', None, 1),
        ('l', 'l', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        ('Enter', None, 'enter', 2.2),
    ]
    LINE_4 = [
        ('Shift', None, 'shift_L', 2.5),  ('z', 'z', None, 1),    ('x', 'x', None, 1),
        ('c', 'c', None, 1),    ('v', 'v', None, 1),    ('b', 'b', None, 1),
        ('n', 'n', None, 1),    ('m', 'm', None, 1),    ('<', '<', None, 1),
        ('>', '>', None, 1),    ('?', '?', None, 1),    ('Shift', None, 'shift_R', 2.5),
    ]
    LINE_5 = [
        ('Ctrl', None, 'ctrl_L', 1.5),  ('Meta', None, 'meta_L', 1.5), ('Alt', None, 'alt_L', 1.5),
        ('', ' ', None, 4.5),  ('Alt', None, 'alt_R', 1.5),    ('Meta', None, 'meta_R', 1.5),
        ('Menu', None, 'menu', 1.5),  ('Ctrl', None, 'ctrl_R', 1.5),
    ]

class MTVKeyboard(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (600, 200))
        kwargs.setdefault('layout', KeyboardLayoutQWERTY())
        super(MTVKeyboard, self).__init__(**kwargs)
        self.layout = kwargs.get('layout')
        self.fbo = Fbo(size=self.size)
        self.need_update = True

    def update(self):
        keysize = Vector(self.width / 15, self.height / 5)
        m = 1
        self.fbo.bind()
        set_color(.1, .1, .1)
        x, y = 0, self.height - keysize.y
        for index in xrange(1, 6):
            line = self.layout.__getattribute__('LINE_%d' % index)
            for key in line:
                displayed_str, internal_str, internal_action, scale = key
                kw = keysize.x * scale
                drawRectangle(pos=(x+m, y+m), size=(kw-m*2, keysize.y-m*2))
                drawLabel(label=displayed_str,
                          pos=(x + kw / 2., y + keysize.y / 2.),
                          font_size=10, bold=False)
                x += kw
            y -= keysize.y
            x = 0
        self.fbo.release()
        self.need_update = False

    def draw(self):
        if self.need_update:
            self.update()
        set_color(1, 1, 1, 1)
        drawTexturedRectangle(texture=self.fbo.texture, size=self.size)

if __name__ == '__main__':
    m = MTWindow()
    m.add_widget(MTVKeyboard())
    runTouchApp()
