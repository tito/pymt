# A rewrite of MTVKeyboard with pills.
# Should really speed up.
# Work in progress !

from pymt import *

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
        ('+', '+', None, 1),    ('Backspace', None, 'backspace', 2),
    ]
    NORMAL_2 = [
        ('Tab', chr(0x09), None, 1.5),  ('q', 'q', None, 1),    ('w', 'w', None, 1),
        ('e', 'e', None, 1),    ('r', 'r', None, 1),    ('t', 't', None, 1),
        ('y', 'y', None, 1),    ('u', 'u', None, 1),    ('i', 'i', None, 1),
        ('o', 'o', None, 1),    ('p', 'p', None, 1),    ('{', '{', None, 1),
        ('}', '}', None, 1),    ('|', '|', None, 1.5)
    ]
    NORMAL_3 = [
        ('Caps Lock', None, 'capslook', 1.8),  ('a', 'a', None, 1),    ('s', 's', None, 1),
        ('d', 'd', None, 1),    ('f', 'f', None, 1),    ('g', 'g', None, 1),
        ('h', 'h', None, 1),    ('j', 'j', None, 1),    ('k', 'k', None, 1),
        ('l', 'l', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        ('Enter', None, 'enter', 2.2),
    ]
    NORMAL_4 = [
        ('Shift', None, 'shift_L', 2.5),  ('z', 'z', None, 1),    ('x', 'x', None, 1),
        ('c', 'c', None, 1),    ('v', 'v', None, 1),    ('b', 'b', None, 1),
        ('n', 'n', None, 1),    ('m', 'm', None, 1),    ('<', '<', None, 1),
        ('>', '>', None, 1),    ('?', '?', None, 1),    ('Shift', None, 'shift_R', 2.5),
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
        ('=', '=', None, 1),    ('Backspace', None, 'backspace', 2),
    ]
    SHIFT_2 = [
        ('Tab', chr(0x09), None, 1.5),  ('Q', 'Q', None, 1),    ('W', 'W', None, 1),
        ('E', 'E', None, 1),    ('R', 'R', None, 1),    ('T', 'T', None, 1),
        ('Y', 'Y', None, 1),    ('U', 'U', None, 1),    ('I', 'I', None, 1),
        ('O', 'O', None, 1),    ('P', 'P', None, 1),    ('[', '[', None, 1),
        (']', ']', None, 1),    ('?', '?', None, 1.5)
    ]
    SHIFT_3 = [
        ('Caps Lock', None, 'capslook', 1.8),  ('A', 'A', None, 1),    ('S', 'S', None, 1),
        ('D', 'D', None, 1),    ('F', 'F', None, 1),    ('G', 'G', None, 1),
        ('H', 'H', None, 1),    ('J', 'J', None, 1),    ('K', 'K', None, 1),
        ('L', 'L', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        ('Enter', None, 'enter', 2.2),
    ]
    SHIFT_4 = [
        ('Shift', None, 'shift_L', 2.5),  ('Z', 'Z', None, 1),    ('X', 'X', None, 1),
        ('C', 'C', None, 1),    ('V', 'V', None, 1),    ('B', 'B', None, 1),
        ('N', 'N', None, 1),    ('M', 'M', None, 1),    (',', ',', None, 1),
        ('.', '.', None, 1),    ('/', '/', None, 1),    ('Shift', None, 'shift_R', 2.5),
    ]
    SHIFT_5 = [
        ('Ctrl', None, 'ctrl_L', 1.5),  ('Meta', None, 'meta_L', 1.5), ('Alt', None, 'alt_L', 1.5),
        ('', ' ', None, 4.5),  ('Alt', None, 'alt_R', 1.5),    ('Meta', None, 'meta_R', 1.5),
        ('Menu', None, 'menu', 1.5),  ('Ctrl', None, 'ctrl_R', 1.5),
    ]

class MTVKeyboard(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (700, 200))
        kwargs.setdefault('layout', KeyboardLayoutQWERTY())
        super(MTVKeyboard, self).__init__(**kwargs)
        self.layout = kwargs.get('layout')
        self.need_update = True
        self.mode = 'NORMAL'
        self.margin = (1, 50, 1, 50) # TRBL
        self.cache = {}
        self.keystyle = {
            'border-radius': 5,
            'border-radius-precision': .1,
            'draw-border': 1,
            'draw-alpha-background': 1,
            'alpha-background': (1, 2, 1, 1),
        }

    def update(self):
        self.texsize = Vector(1536, 512)
        self.keysize = Vector(self.texsize.x / 15, self.texsize.y / 5)

        # create fbo if not exist for this layout / mode
        layoutmode = '%s:%s' % (self.layout.NAME, self.mode)
        if not layoutmode in self.cache:
            fbo = Fbo(size=self.texsize)
            self.cache[layoutmode] = fbo
            self.fbo = fbo
        else:
            self.fbo = self.cache[layoutmode]
        # draw onto fbo
        m = 3
        self.fbo.bind()
        x, y = 0, self.texsize.y - self.keysize.y
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
                    drawCSSRectangle(pos=(x+m, y+m), size=(kw-m*2, self.keysize.y-m*2), style=self.keystyle)
                    drawLabel(label=displayed_str,
                            pos=(x + kw / 2., y + self.keysize.y / 2.),
                            font_size=20, bold=False)
                # advance X
                x += kw
            # advance Y
            y -= self.keysize.y
            x = 0
        # update completed
        self.fbo.release()
        self.need_update = False

    def draw(self):
        if self.need_update:
            self.update()
        set_color(*self.style['bg-color'])
        drawCSSRectangle(size=self.size, style=self.style)
        set_color(1, 1, 1)
        drawTexturedRectangle(texture=self.fbo.texture, pos=(self.margin[3], self.margin[2]),
                size=(self.width - self.margin[1] - self.margin[3],
                    self.height - self.margin[0] - self.margin[2]))

    def get_key_at_pos(self, x, y):
        if x < self.margin[3] or x > self.width - self.margin[1] or \
           y < self.margin[2] or y > self.height - self.margin[0]:
               return None
        index = 5-int((y - self.margin[2]) /
                (self.height - self.margin[0] - self.margin[2])
                * 5.)
        line = self.layout.__getattribute__('%s_%d' % (self.mode, index))
        x -= self.margin[3]
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
            self.need_update = True
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
