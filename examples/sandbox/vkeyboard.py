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
    key-color: rgba(20, 20, 20, 255);
    syskey-color: rgba(20, 20, 40, 255);
}
'''

css_add_sheet(vkeyboard_css)

class KeyboardLayout(object):
    ID = 'nolayout'
    DESCRIPTION = 'nodescription'
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
    ID = 'qwerty'
    TITLE = 'Qwerty'
    DESCRIPTION = 'A classical US Keyboard'
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
        (u'\u21ea', None, 'capslock', 1.8),  ('a', 'a', None, 1),    ('s', 's', None, 1),
        ('d', 'd', None, 1),    ('f', 'f', None, 1),    ('g', 'g', None, 1),
        ('h', 'h', None, 1),    ('j', 'j', None, 1),    ('k', 'k', None, 1),
        ('l', 'l', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        (u'\u23ce', None, 'enter', 2.2),
    ]
    NORMAL_4 = [
        (u'\u21e7', None, 'shift_L', 2.5),  ('z', 'z', None, 1),    ('x', 'x', None, 1),
        ('c', 'c', None, 1),    ('v', 'v', None, 1),    ('b', 'b', None, 1),
        ('n', 'n', None, 1),    ('m', 'm', None, 1),    ('<', '<', None, 1),
        ('>', '>', None, 1),    ('?', '?', None, 1),    (u'\u21e7', None, 'shift_R', 2.5),
    ]
    NORMAL_5 = [
        ('', ' ', None, 13.5), (u'\u2b12', None, 'layout', 1.5),
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
        (u'\u21ea', None, 'capslock', 1.8),  ('A', 'A', None, 1),    ('S', 'S', None, 1),
        ('D', 'D', None, 1),    ('F', 'F', None, 1),    ('G', 'G', None, 1),
        ('H', 'H', None, 1),    ('J', 'J', None, 1),    ('K', 'K', None, 1),
        ('L', 'L', None, 1),    (':', ':', None, 1),    ('"', '"', None, 1),
        (u'\u23ce', None, 'enter', 2.2),
    ]
    SHIFT_4 = [
        (u'\u21e7', None, 'shift_L', 2.5),  ('Z', 'Z', None, 1),    ('X', 'X', None, 1),
        ('C', 'C', None, 1),    ('V', 'V', None, 1),    ('B', 'B', None, 1),
        ('N', 'N', None, 1),    ('M', 'M', None, 1),    (',', ',', None, 1),
        ('.', '.', None, 1),    ('/', '/', None, 1),    (u'\u21e7', None, 'shift_R', 2.5),
    ]
    SHIFT_5 = [
        ('', ' ', None, 13.5), (u'\u2b12', None, 'layout', 1.5),
    ]

class MTVKeyboard(MTScatterWidget):

    available_layout = [KeyboardLayoutQWERTY]

    def __init__(self, **kwargs):
        '''
        MTVKeyboard is a OnBoard keyboard, who support Multitouch.
        Layout are entirely customizable, and you can switch from layout with
        little button in bottom-right of keyboard.

        :Events:
            `on_key_down` : key
                Fired when a key is down
                The key contain: displayed_str, internal_str, internal_action, width
            `on_key_up` : key
                Fired when a key is up
                The key contain: displayed_str, internal_str, internal_action, width
            `on_text_change` : text
                Fired when the internal text is changed
        '''
        kwargs.setdefault('size', (700, 200))
        kwargs.setdefault('layout', KeyboardLayoutQWERTY())

        # we forbid scaling from scatter
        # cause we'll handle it in a special manner (lazy update)
        kwargs['do_scale'] = False
        super(MTVKeyboard, self).__init__(**kwargs)

        self.register_event_type('on_key_down')
        self.register_event_type('on_key_up')
        self.register_event_type('on_text_change')

        self.layout             = kwargs.get('layout')
        self.container_width, self.container_height   = self.size

        self._mode              = 'NORMAL'
        self._cache             = {}
        self._current_cache     = None
        self._last_update       = 0
        self._last_update_scale = 1.
        self._need_update       = 'now'
        self._internal_text     = ''
        self._show_layout       = False
        self._active_keys       = []

        # prepare layout widget
        mtop, mright, mbottom, mleft = self.style['margin']
        self._layout_widget     = MTKineticList(
            title=None, searchable=False, deletable=False,
            size=(self.width - mleft - mright, self.height),
            pos=(mleft, 0), style={'bg-color': (.0, .0, .0, .7)},
            visible=False)
        for layout in MTVKeyboard.available_layout:
            item = MTKineticItem(label=layout.TITLE + ' - ' + layout.DESCRIPTION,
                    style={'font-size':12}, size=(self.width - mleft - mright, 40))
            self._layout_widget.add_widget(item, curry(self.on_layout_change, layout))
        self.add_widget(self._layout_widget)


    #
    # Static methods
    #

    @staticmethod
    def add_custom_layout(layout_class):
        if not layout_class in MTVKeyboard.available_layout:
            MTVKeyboard.available_layout.append(layout_class)

    #
    # Keyboard properties
    #

    def _get_text(self):
        return self._internal_text
    def _set_text(self, value):
        if value != self._internal_text:
            self._internal_text = value
            self.dispatch_event('on_text_change', value)
    text = property(_get_text, _set_text,
            doc='''Get/set text string on vkeyboard''')

    def _get_mode(self):
        return self._mode
    def _set_mode(self, value):
        if value != self._mode:
            self._need_update = 'now'
            self._mode = value
    mode = property(_get_mode, _set_mode,
            doc='''Get/set mode of vkeyboard (NORMAL, SHIFT...)''')

    #
    # Public methods
    #

    def clear(self):
        '''Clear the text'''
        self._internal_text = ''


    #
    # Private methods
    #

    def _lazy_update(self):
        self._need_update = 'lazy'
        self._last_update = clock.get_default().time()

    def _update(self):
        dt = clock.get_default().time() - self._last_update
        if self._need_update is None:
            return

        if self._need_update == 'now' or (self._need_update == 'lazy' and  dt > 0.9):
            # create layout mode if not in cache
            layoutmode = '%s:%s' % (self.layout.ID, self.mode)
            if not layoutmode in self._cache:
                self._cache[layoutmode] = {'background': GlDisplayList(), 'keys': GlDisplayList()}
            self._current_cache = self._cache[layoutmode]

            # do real update
            self._do_update(mode='background')
            self._do_update(mode='keys')

            # don't update too fast next time (if it's lazy)
            self._last_update = clock.get_default().time()
            self._last_update_scale = self.get_scale_factor()
            self._need_update = None

    def _do_update(self, mode=None):
        # we absolutly want mode to update displaylist.
        if mode not in ('background', 'keys'):
            return

        # don't update background if it's already compiled
        if mode == 'background' and self._current_cache['background'].is_compiled():
            return

        # calculate margin
        s = self.get_scale_factor()
        w, h = self.container_width, self.container_height
        if mode == 'background':
            s = 1.
            w, h = self.size
        mtop, mright, mbottom, mleft = map(lambda x: x * s, self.style['margin'])
        self.texsize = Vector(w - mleft - mright,
                              h - mtop - mbottom)
        self.keysize = Vector(self.texsize.x / 15, self.texsize.y / 5)
        m = 3 * s
        x, y = 0, self.texsize.y - self.keysize.y

        # update display list
        with self._current_cache[mode]:

            # draw lines
            for index in xrange(1, 6):
                line = self.layout.__getattribute__('%s_%d' % (self.mode, index))

                # draw keys
                for key in line:
                    displayed_str, internal_str, internal_action, scale = key
                    kw = self.keysize.x * scale

                    # don't display empty keys
                    if displayed_str is not None:
                        set_color(*self.style['key-color'])
                        if mode == 'background':
                            if internal_action is not None:
                                set_color(*self.style['syskey-color'])
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
        self._need_update = None

    #
    # Rewrite some handle to update the widget (drawing and scalling)
    #

    def on_resize(self, w, h):
        self.container_width, self.container_height = w, h
        self._lazy_update()

    def on_layout_change(self, layout, *largs):
        self._layout_widget.visible = False
        self.layout = layout()
        self._update()

    def collide_point(self, x, y):
        local_coords = self.to_local(x, y)
        if local_coords[0] > 0 and local_coords[0] < self.container_width \
           and local_coords[1] > 0 and local_coords[1] < self.container_height:
            return True
        else:
            return False


    def draw(self):
        self._update()

        # background
        set_color(*self.style['bg-color'])
        drawCSSRectangle(size=(self.container_width, self.container_height), style=self.style)

        # content dynamic update
        with gx_matrix:
            s = self.get_scale_factor()
            glTranslatef(self.style['margin'][3] * s, self.style['margin'][2] * s, 0)
            with gx_matrix:
                glScalef(s, s, s)
                self._current_cache['background'].draw()
            scale_factor = self.get_scale_factor() / self._last_update_scale
            glScalef(scale_factor, scale_factor, scale_factor)
            self._current_cache['keys'].draw()

    def get_key_at_pos(self, x, y):
        '''Return the key on the current layout, at the coordinate (x, y)'''
        mtop, mright, mbottom, mleft = self.style['margin']
        w, h = self.width - mleft - mright, self.height - mtop - mbottom
        keysize = Vector(w / 15, h / 5)
        if x < mleft or x > self.width - mright or \
           y < mbottom or y > self.height - mtop:
               return None
        index = 5-int((y - mbottom) /
                (self.height - mtop - mbottom)
                * 5.)
        line = self.layout.__getattribute__('%s_%d' % (self.mode, index))
        x -= mleft
        kx = 0
        for key in line:
            kw = keysize.x * key[3]
            if x >= kx and x < kx + kw:
                return key
            kx += kw
        return None

    def on_key_down(self, key):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            if internal_str is not None:
                self._internal_text += internal_str
        elif internal_action in ('capslock'):
            if self.mode == 'NORMAL':
                self.mode = 'SHIFT'
            else:
                self.mode = 'NORMAL'
            self._need_update = 'now'
            return
        elif internal_action in ('shift', 'shift_L', 'shift_R'):
            if self.mode == 'NORMAL':
                self.mode = 'SHIFT'
            else:
                self.mode = 'NORMAL'
            self._need_update = 'now'
            return
        elif internal_action in ('layout'):
            self._layout_widget.visible = True
        elif internal_action in ('backspace'):
            self._internal_text = self._internal_text[:-1]

    def on_key_up(self, key):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            pass
        elif internal_action in ('shift', 'shift_L', 'shift_R'):
            if self.mode == 'NORMAL':
                self.mode = 'SHIFT'
            else:
                self.mode = 'NORMAL'
            self._need_update = 'now'
            return

    def on_touch_down(self, touch):
        if not self._layout_widget.visible:
            x, y = [x / self.get_scale_factor() for x in self.to_local(touch.x, touch.y)]
            key = self.get_key_at_pos(x, y)
            if key is not None:
                if key not in self._active_keys:
                    touch.userdata['vkeyboard_key'] = key
                    self._active_keys.append(key)
                    self.dispatch_event('on_key_down', key)
                return True
        return super(MTVKeyboard, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if 'vkeyboard_key' in touch.userdata:
            key = touch.userdata['vkeyboard_key']
            if key in self._active_keys:
                self._active_keys.remove(key)
            self.dispatch_event('on_key_up', key)
            return True
        return super(MTVKeyboard, self).on_touch_up(touch)


if __name__ == '__main__':
    m = MTWindow()
    m.add_widget(MTVKeyboard())
    runTouchApp()
