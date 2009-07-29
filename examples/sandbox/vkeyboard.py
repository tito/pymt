# A rewrite of MTVKeyboard with pills.
# Should really speed up.
# Work in progress !

from __future__ import with_statement
from pymt import *
import os
from pyglet import clock
from pyglet import font
from pyglet.gl import glScalef, glTranslatef

vkeyboard_fontname = os.path.join(pymt_data_dir, 'DejaVuSans.ttf')
font.add_file(vkeyboard_fontname)

vkeyboard_css = '''
vkeyboard {
    margin: 10 50 10 50;
    border-radius: 15;
    border-radius-precision: 0.35;
    key-border-radius: 5;
    key-border-radius-precision: 1;
    draw-key-border: 1;
    key-alpha-background: 1 1 .7 .7;
    draw-key-alpha-background: 1;
    draw-border: 1;
}
'''

css_add_sheet(vkeyboard_css)

class KeyboardLayout(object):
    NAME = 'nolayout'
    NORMAL_1 = []
    NORMAL_2 = []
    NORMAL_3 = []
    NORMAL_4 = []
    NORMAL_5 = []
    SHIFT_1 = []
    SHIFT_2 = []
    SHIFT_3 = []
    SHIFT_4 = []
    SHIFT_5 = []

class KeyboardLayoutQWERTY(KeyboardLayout):
    NAME = 'qwerty'
    NORMAL_1 = [
        ('~', '~', None, 1),    ('!', '!', None, 1),    ('@', '@', None, 1),
        ('#', '#', None, 1),    ('$', '$', None, 1),    ('%', '%', None, 1),
        ('^', '^', None, 1),    ('&', '&', None, 1),    ('*', '*', None, 1),
        ('(', '(', None, 1),    (')', ')', None, 1),    ('_', '_', None, 1),
        ('+', '+', None, 1),    (u'\u21e6', None, 'backspace', 2),
    ]
    NORMAL_2 = [
        (u'\u21B9', chr(0x09), None, 1.5),  ('q', 'q', None, 1),    ('w', 'w', None, 1),
        ('e', 'e', None, 1),    ('r', 'r', None, 1),    ('t', 't', None, 1),
        ('y', 'y', None, 1),    ('u', 'u', None, 1),    ('i', 'i', None, 1),
        ('o', 'o', None, 1),    ('p', 'p', None, 1),    ('{', '{', None, 1),
        ('}', '}', None, 1),    ('|', '|', None, 1.5)
    ]
    NORMAL_3 = [
        (u'\u21ea', None, 'capslook', 1.8),  ('a', 'a', None, 1),    ('s', 's', None, 1),
        ('d', 'd', None, 1),    ('f', 'f', None, 1),    ('g', 'g', None, 1),
        ('h', 'h', None, 1),    ('j', 'j', None, 1),    ('k', 'k', None, 1),
        ('l', 'l', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        ('Enter', None, 'enter', 2.2),
    ]
    NORMAL_4 = [
        (u'\u21e7', None, 'shift_L', 2.5),  ('z', 'z', None, 1),    ('x', 'x', None, 1),
        ('c', 'c', None, 1),    ('v', 'v', None, 1),    ('b', 'b', None, 1),
        ('n', 'n', None, 1),    ('m', 'm', None, 1),    ('<', '<', None, 1),
        ('>', '>', None, 1),    ('?', '?', None, 1),    (u'\u21e7', None, 'shift_R', 2.5),
    ]
    NORMAL_5 = [
        ('Ctrl', None, 'ctrl_L', 1.5),  ('Meta', None, 'meta_L', 1.5), ('Alt', None, 'alt_L', 1.5),
        ('', ' ', None, 4.5),  ('Alt', None, 'alt_R', 1.5),    ('Meta', None, 'meta_R', 1.5),
        ('Menu', None, 'menu', 1.5),  ('Ctrl', None, 'ctrl_R', 1.5),
    ]
    SHIFT_1 = [
        ('`', '`', None, 1),    ('1', '1', None, 1),    ('2', '2', None, 1),
        ('3', '3', None, 1),    ('4', '4', None, 1),    ('5', '5', None, 1),
        ('6', '6', None, 1),    ('7', '7', None, 1),    ('8', '8', None, 1),
        ('9', '9', None, 1),    ('0', '0', None, 1),    ('+', '+', None, 1),
        ('=', '=', None, 1),    (u'\u21e6', None, 'backspace', 2),
    ]
    SHIFT_2 = [
        (u'\u21B9', chr(0x09), None, 1.5),  ('Q', 'Q', None, 1),    ('W', 'W', None, 1),
        ('E', 'E', None, 1),    ('R', 'R', None, 1),    ('T', 'T', None, 1),
        ('Y', 'Y', None, 1),    ('U', 'U', None, 1),    ('I', 'I', None, 1),
        ('O', 'O', None, 1),    ('P', 'P', None, 1),    ('[', '[', None, 1),
        (']', ']', None, 1),    ('?', '?', None, 1.5)
    ]
    SHIFT_3 = [
        (u'\u21ea', None, 'capslook', 1.8),  ('A', 'A', None, 1),    ('S', 'S', None, 1),
        ('D', 'D', None, 1),    ('F', 'F', None, 1),    ('G', 'G', None, 1),
        ('H', 'H', None, 1),    ('J', 'J', None, 1),    ('K', 'K', None, 1),
        ('L', 'L', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        ('Enter', None, 'enter', 2.2),
    ]
    SHIFT_4 = [
        (u'\u21e7', None, 'shift_L', 2.5),  ('Z', 'Z', None, 1),    ('X', 'X', None, 1),
        ('C', 'C', None, 1),    ('V', 'V', None, 1),    ('B', 'B', None, 1),
        ('N', 'N', None, 1),    ('M', 'M', None, 1),    (',', ',', None, 1),
        ('.', '.', None, 1),    ('/', '/', None, 1),    (u'\u21e7', None, 'shift_R', 2.5),
    ]
    SHIFT_5 = [
        ('Ctrl', None, 'ctrl_L', 1.5),  ('Meta', None, 'meta_L', 1.5), ('Alt', None, 'alt_L', 1.5),
        ('', ' ', None, 4.5),  ('Alt', None, 'alt_R', 1.5),    ('Meta', None, 'meta_R', 1.5),
        ('Menu', None, 'menu', 1.5),  ('Ctrl', None, 'ctrl_R', 1.5),
    ]

class MTVKeyboard(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('do_scale', False)
        kwargs.setdefault('size', (700, 200))
        kwargs.setdefault('layout', KeyboardLayoutQWERTY())
        super(MTVKeyboard, self).__init__(**kwargs)
        self.layout = kwargs.get('layout')
        self.mode = 'NORMAL'
        self.cache = {}
        self.container_width, self.container_height = self.size
        self.last_update = 0
        self.last_update_scale = 1.
        self.need_update = 'now'

    def on_resize(self, w, h):
        self.container_width, self.container_height = w, h
        self.lazy_update()

    def to_local(self, x, y):
        x, y = super(MTVKeyboard, self).to_local(x, y)
        return map(lambda x: x * self.get_scale_factor(), (x, y))

    def lazy_update(self):
        self.need_update = 'lazy'
        self.last_update = clock.get_default().time()

    def update(self):
        dt = clock.get_default().time() - self.last_update
        if self.need_update is not None and \
            (self.need_update == 'now' or (self.need_update == 'lazy' and  dt > 0.9)):
            # create layout mode if not in cache
            layoutmode = '%s:%s' % (self.layout.NAME, self.mode)
            if not layoutmode in self.cache:
                self.cache[layoutmode] = {'background': GlDisplayList(), 'keys': GlDisplayList()}
            self.current_cache = self.cache[layoutmode]
            # do real update
            self.do_update(mode='background')
            self.do_update(mode='keys')
            # don't update too fast next time (if it's lazy)
            self.last_update = clock.get_default().time()
            self.last_update_scale = self.get_scale_factor()
            self.need_update = None

    def do_update(self, mode=None):
        # we absolutly want mode to update displaylist.
        if mode not in ('background', 'keys'):
            return

        # don't update background if it's already compiled
        if mode == 'background' and self.current_cache['background'].is_compiled():
            return

        # calculate margin
        s = self.get_scale_factor()
        if mode == 'background':
            s = 1.
        mtop, mright, mbottom, mleft = map(lambda x: x * s, self.style['margin'])
        self.texsize = Vector(self.container_width - mleft - mright,
                              self.container_height - mtop - mbottom)
        self.keysize = Vector(self.texsize.x / 15, self.texsize.y / 5)
        m = 3 * s
        x, y = 0, self.texsize.y - self.keysize.y

        # update display list
        with self.current_cache[mode]:
            # draw lines
            for index in xrange(1, 6):
                line = self.layout.__getattribute__('%s_%d' % (self.mode, index))
                # draw keys
                for key in line:
                    displayed_str, internal_str, internal_action, scale = key
                    kw = self.keysize.x * scale
                    # don't display empty keys
                    if displayed_str is not None:
                        set_color(.1, .1, .1)
                        if mode == 'background':
                            if internal_action is not None:
                                set_color(.1, .1, .15)
                            drawCSSRectangle(
                                pos=(x+m, y+m),
                                size=(kw-m*2, self.keysize.y-m*2),
                                style=self.style, prefix='key')
                        elif mode == 'keys':
                            font_size = 14 * s
                            if font_size < 8:
                                font_size = 8
                            drawLabel(label=displayed_str,
                                    pos=(x + kw / 2., y + self.keysize.y / 2.),
                                    font_size=font_size, bold=False,
                                    font_name='DejaVu Sans')
                    # advance X
                    x += kw
                # advance Y
                y -= self.keysize.y
                x = 0

        # update completed
        self.need_update = None

    def draw(self):

        self.update()

        # background
        set_color(*self.style['bg-color'])
        drawCSSRectangle(size=(self.container_width, self.container_height), style=self.style)

        # content dynamic update
        with gx_matrix:
            s = self.get_scale_factor()
            glTranslatef(self.style['margin'][3] * s, self.style['margin'][2] * s, 0)
            with gx_matrix:
                glScalef(s, s, s)
                self.current_cache['background'].draw()
            scale_factor = self.get_scale_factor() / self.last_update_scale
            glScalef(scale_factor, scale_factor, scale_factor)
            self.current_cache['keys'].draw()

    def get_key_at_pos(self, x, y):
        top, right, bottom, left = self.style['margin']
        if x < left or x > self.width - right or \
           y < bottom or y > self.height - top:
               return None
        index = 5-int((y - bottom) /
                (self.height - top - bottom)
                * 5.)
        line = self.layout.__getattribute__('%s_%d' % (self.mode, index))
        x -= left
        kx = 0
        for key in line:
            kw = self.keysize.x * key[3]
            if x >= kx and x < kx + kw:
                return key
            kx += kw
        return None

    def do_key(self, key):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            pass
        elif internal_action in ('capslook'):
            if self.mode == 'NORMAL':
                self.mode = 'SHIFT'
            else:
                self.mode = 'NORMAL'
            self.need_update = 'now'
            return

    def on_touch_down(self, touch):
        key = self.get_key_at_pos(*self.to_local(touch.x, touch.y))
        if key is not None:
            self.do_key(key)
            return True
        return super(MTVKeyboard, self).on_touch_down(touch)


if __name__ == '__main__':
    m = MTWindow()
    m.add_widget(MTVKeyboard())
    runTouchApp()
