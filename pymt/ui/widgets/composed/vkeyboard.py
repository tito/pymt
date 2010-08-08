'''
VKeyboard: Virtual keyboard with custom layout support
'''


import os
import pymt
from pymt.base import getFrameDt
from pymt.graphx import set_color, drawCSSRectangle, drawLabel, GlDisplayList, \
        gx_matrix, getLastLabel
from pymt.clock import getClock
from pymt.utils import curry
from pymt.vector import Vector
from pymt.ui.widgets.scatter import MTScatterWidget
from pymt.ui.widgets.composed.kineticlist import MTKineticList, MTKineticItem
from OpenGL.GL import glScalef, glTranslatef

__all__ = ('MTVKeyboard', 'KeyboardLayout', 'KeyboardLayoutQWERTY',
           'KeyboardLayoutAZERTY')

class KeyboardLayout(object):
    '''Base for all Keyboard Layout'''
    ID              = 'nolayout'
    TITLE           = 'nolayout'
    DESCRIPTION     = 'nodescription'
    FONT_FILENAME   = None
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
    # Actual letters. No numbers or special chars or keys. Upper & lower.
    LETTERS = []

class KeyboardLayoutQWERTY(KeyboardLayout):
    '''Implementation of QWERTY Layout'''
    ID              = 'qwerty'
    TITLE           = 'Qwerty'
    DESCRIPTION     = 'A classical US Keyboard'
    SIZE            = (15, 5)
    NORMAL_1 = [
        ('`', '`', None, 1),    ('1', '1', None, 1),    ('2', '2', None, 1),
        ('3', '3', None, 1),    ('4', '4', None, 1),    ('5', '5', None, 1),
        ('6', '6', None, 1),    ('7', '7', None, 1),    ('8', '8', None, 1),
        ('9', '9', None, 1),    ('0', '0', None, 1),    ('+', '+', None, 1),
        ('=', '=', None, 1),    (u'\u232b', None, 'backspace', 2),
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
        (' ', ' ', None, 12), (u'\u2b12', None, 'layout', 1.5), (u'\u2a2f', None, 'escape', 1.5),

    ]
    SHIFT_1 = [
        ('~', '~', None, 1),    ('!', '!', None, 1),    ('@', '@', None, 1),
        ('#', '#', None, 1),    ('$', '$', None, 1),    ('%', '%', None, 1),
        ('^', '^', None, 1),    ('&', '&', None, 1),    ('*', '*', None, 1),
        ('(', '(', None, 1),    (')', ')', None, 1),    ('_', '_', None, 1),
        ('+', '+', None, 1),    (u'\u232b', None, 'backspace', 2),
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
        (' ', ' ', None, 12), (u'\u2b12', None, 'layout', 1.5), (u'\u2a2f', None, 'escape', 1.5),
    ]

    LETTERS = NORMAL_2[1:11] + NORMAL_3[1:10] + NORMAL_4[1:8] + \
              SHIFT_2[1:11] + SHIFT_3[1:10] + SHIFT_4[1:8]


class KeyboardLayoutAZERTY(KeyboardLayout):
    '''Implementation of AZERTY Layout'''
    ID              = 'azerty'
    TITLE           = 'Azerty'
    DESCRIPTION     = 'A French keyboard without international keys'
    SIZE            = (15, 5)
    NORMAL_1 = [
        ('@', '@', None, 1),    ('&', '&', None, 1),    (u'\xe9', u'\xe9', None, 1),
        ('"', '"', None, 1),    ('\'', '\'', None, 1),  ('(', '(', None, 1),
        ('-', '-', None, 1),    (u'\xe8', u'\xe8', None, 1),    ('_', '_', None, 1),
        (u'\xe7', u'\xe7', None, 1),    (u'\xe0', u'\xe0', None, 1),    (')', ')', None, 1),
        ('=', '=', None, 1),    (u'\u232b', None, 'backspace', 2),
    ]
    NORMAL_2 = [
        (u'\u21B9', chr(0x09), None, 1.5),  ('a', 'a', None, 1),    ('z', 'z', None, 1),
        ('e', 'e', None, 1),    ('r', 'r', None, 1),    ('t', 't', None, 1),
        ('y', 'y', None, 1),    ('u', 'u', None, 1),    ('i', 'i', None, 1),
        ('o', 'o', None, 1),    ('p', 'p', None, 1),    ('^', '^', None, 1),
        ('$', '$', None, 1),    (u'\u23ce', None, 'enter', 1.5),
    ]
    NORMAL_3 = [
        (u'\u21ea', None, 'capslock', 1.8),  ('q', 'q', None, 1),    ('s', 's', None, 1),
        ('d', 'd', None, 1),    ('f', 'f', None, 1),    ('g', 'g', None, 1),
        ('h', 'h', None, 1),    ('j', 'j', None, 1),    ('k', 'k', None, 1),
        ('l', 'l', None, 1),    ('m', 'm', None, 1),    (u'\xf9', u'\xf9', None, 1),
        ('*', '*', None, 1),    (u'\u23ce', None, 'enter', 1.2),
    ]
    NORMAL_4 = [
        (u'\u21e7', None, 'shift_L', 1.5),  ('<', '<', None, 1),    ('w', 'w', None, 1),
        ('x', 'x', None, 1),
        ('c', 'c', None, 1),    ('v', 'v', None, 1),    ('b', 'b', None, 1),
        ('n', 'n', None, 1),    (',', ',', None, 1),    (';', ';', None, 1),
        (':', ':', None, 1),    ('!', '!', None, 1),    (u'\u21e7', None, 'shift_R', 2.5),
    ]
    NORMAL_5 = [
        (' ', ' ', None, 12), (u'\u2b12', None, 'layout', 1.5), (u'\u2a2f', None, 'escape', 1.5),
    ]
    SHIFT_1 = [
        ('|', '|', None, 1),    ('1', '1', None, 1),    ('2', '2', None, 1),
        ('3', '3', None, 1),    ('4', '4', None, 1),    ('5', '5', None, 1),
        ('6', '6', None, 1),    ('7', '7', None, 1),    ('8', '8', None, 1),
        ('9', '9', None, 1),    ('0', '0', None, 1),    ('#', '#', None, 1),
        ('+', '+', None, 1),    (u'\u232b', None, 'backspace', 2),
    ]
    SHIFT_2 = [
        (u'\u21B9', chr(0x09), None, 1.5),  ('A', 'A', None, 1),    ('Z', 'Z', None, 1),
        ('E', 'E', None, 1),    ('R', 'R', None, 1),    ('T', 'T', None, 1),
        ('Y', 'Y', None, 1),    ('U', 'U', None, 1),    ('I', 'I', None, 1),
        ('O', 'O', None, 1),    ('P', 'P', None, 1),    ('[', '[', None, 1),
        (']', ']', None, 1),    (u'\u23ce', None, 'enter', 1.5),
    ]
    SHIFT_3 = [
        (u'\u21ea', None, 'capslock', 1.8),  ('Q', 'Q', None, 1),    ('S', 'S', None, 1),
        ('D', 'D', None, 1),    ('F', 'F', None, 1),    ('G', 'G', None, 1),
        ('H', 'H', None, 1),    ('J', 'J', None, 1),    ('K', 'K', None, 1),
        ('L', 'L', None, 1),    ('M', 'M', None, 1),    ('%', '%', None, 1),
        (u'\xb5', u'\xb5', None, 1),    (u'\u23ce', None, 'enter', 1.2),
    ]
    SHIFT_4 = [
        (u'\u21e7', None, 'shift_L', 1.5),  ('>', '>', None, 1),    ('W', 'W', None, 1),
        ('X', 'X', None, 1),    ('C', 'C', None, 1),    ('V', 'V', None, 1),
        ('B', 'B', None, 1),    ('N', 'N', None, 1),    ('?', '?', None, 1),
        ('.', '.', None, 1),    ('/', '/', None, 1),    (u'\xa7', u'\xa7', None, 1),
        (u'\u21e7', None, 'shift_R', 2.5),
    ]
    SHIFT_5 = [
        (' ', ' ', None, 12), (u'\u2b12', None, 'layout', 1.5), (u'\u2a2f', None, 'escape', 1.5),
    ]

    LETTERS = NORMAL_2[1:11] + NORMAL_3[1:11] + NORMAL_4[2:8] + \
              SHIFT_2[1:11] + SHIFT_3[1:11] + SHIFT_4[2:8]


class MTVKeyboard(MTScatterWidget):
    '''
    MTVKeyboard is an onscreen keyboard with multitouch support.
    Its layout is entirely customizable and you can switch between available
    layouts using a button in the bottom right of the widget.

    :Parameters:
        `layout` : KeyboardLayout object, default to None
            If None, keyboard layout will be created from configuration
            property.
        `time_lazy_update` : float, default to 0.2
            Time in seconds to force a lazy update when keyboard size changes
        `repeat` : float, default to 0.2
            Key repeat rate. 1/15. will repeat the last key 5 times per seconds
        `repeat_timeout` : float, default to 0.2
            Will start to repeat the key after 200ms

    :Events:
        `on_key_down` : key
            Fired when a key is down.
            The key contains: displayed_str, internal_str, internal_action, width
        `on_key_up` : key
            Fired when a key is up.
            The key contains: displayed_str, internal_str, internal_action, width
        `on_text_change` : text
            Fired when the internal text is changed

    List of internal actions available :

    * backspace
    * capslock
    * enter
    * escape
    * layout (to display layout list)
    * shift
    * shift_L
    * shift_R

    '''

    available_layout = []

    DEFAULT_SIZE = (700, 200)
    DEFAULT_POS = (0, 0)

    def __init__(self, **kwargs):
        kwargs.setdefault('size', MTVKeyboard.DEFAULT_SIZE)
        kwargs.setdefault('pos', MTVKeyboard.DEFAULT_POS)
        kwargs.setdefault('layout', None)
        kwargs.setdefault('time_lazy_update', .2)
        kwargs.setdefault('repeat', 1 / 15.)
        kwargs.setdefault('repeat_timeout', .2)

        self._old_scale = 0

        super(MTVKeyboard, self).__init__(**kwargs)

        self.register_event_type('on_key_down')
        self.register_event_type('on_key_up')
        self.register_event_type('on_text_change')

        self.time_lazy_update   = kwargs.get('time_lazy_update')
        self.layout             = kwargs.get('layout')
        self.container_width, self.container_height   = self.size
        self.repeat             = kwargs.get('repeat')
        self.repeat_timeout     = kwargs.get('repeat_timeout')

        # read default layout in configuration
        if self.layout is None:
            idlayout = pymt.pymt_config.get('keyboard', 'layout')
            # search layout
            for layout in MTVKeyboard.available_layout:
                if layout.ID == idlayout:
                    self.layout = layout()
                    break
            # no layout found ?
            if self.layout is None:
                pymt.pymt_logger.warning('Vkeyboard: Keyboard layout <%s> not found, fallback on QWERTY' % idlayout)
                self.layout = KeyboardLayoutQWERTY()

        self._mode              = 'NORMAL'
        self._cache             = {}
        self._current_cache     = None
        self._last_update       = 0
        self._last_update_scale = 1.
        self._need_update       = 'now'
        self._internal_text     = u''
        self._show_layout       = False
        self._active_keys       = []
        self._used_label        = []
        self._last_key_down     = []
        self._last_key_repeat   = 0
        self._last_key_repeat_timeout  = 0

        # prepare layout widget
        mtop, mright, mbottom, mleft = self.style['margin']
        self._layout_widget     = MTKineticList(
            title=None, searchable=False, deletable=False,
            size=(self.width - mleft - mright, self.height),
            pos=(mleft, 0), style={'bg-color': (.0, .0, .0, .7)},
            visible=False)
        for layout in MTVKeyboard.available_layout:
            item = MTKineticItem(label=layout.TITLE + ' - ' + layout.DESCRIPTION,
                    style={'font-size':14}, size=(self.width - mleft - mright, 40))
            item.push_handlers(on_press=curry(self.on_layout_change, layout))
            self._layout_widget.add_widget(item)
        self.add_widget(self._layout_widget)


    def on_text_change(self, *largs):
        pass


    #
    # Static methods
    #

    @staticmethod
    def add_custom_layout(layout_class):
        '''Add a custom layout class on MTVKeyboard'''
        if not layout_class in MTVKeyboard.available_layout:
            # Append layout in class
            MTVKeyboard.available_layout.append(layout_class)
            if layout_class.FONT_FILENAME != None:
                # Load custom font
                try:
                    # XXX FIXME
                    #font.add_file(layout_class.FONT_FILENAME)
                    pass
                except:
                    pymt.pymt_logger.exception('Vkeyboard: Unable to load custom font')

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
        self.text = u''


    #
    # Private methods
    #

    def _lazy_update(self):
        self.container_width = int(self.width * self.scale)
        self.container_height = int(self.height * self.scale)
        self._need_update = 'lazy'
        self._last_update = getClock().get_time()

    def _update(self):
        dt = getClock().get_time() - self._last_update
        if self._need_update is None:
            return

        if self._need_update == 'now' or (self._need_update == 'lazy' and  dt >
                                         self.time_lazy_update):
            # create layout mode if not in cache
            layoutmode = '%s:%s' % (self.layout.ID, self.mode)
            if not layoutmode in self._cache:
                self._cache[layoutmode] = {'background': GlDisplayList(),
                                           'keys': GlDisplayList(),
                                           'usedlabel': []}
            self._current_cache = self._cache[layoutmode]

            # do real update
            self._do_update(mode='background')
            self._do_update(mode='keys')

            # don't update too fast next time (if it's lazy)
            self._last_update = getClock().get_time()
            self._last_update_scale = self.scale
            self._need_update = None

    def _do_update(self, mode=None):
        # we absolutly want mode to update displaylist.
        if mode not in ('background', 'keys'):
            return

        # don't update background if it's already compiled
        if mode == 'background' and self._current_cache['background'].is_compiled():
            return

        # calculate margin
        s = self.scale
        w, h = self.container_width, self.container_height
        if mode == 'background':
            s = 1.
            w, h = self.size
        mtop, mright, mbottom, mleft = map(lambda x: x * s, self.style['margin'])
        self.texsize = Vector(w - mleft - mright,
                              h - mtop - mbottom)
        kx, ky = self.layout.SIZE
        self.keysize = Vector(self.texsize.x / kx, self.texsize.y / ky)
        m = 3 * s
        x, y = 0, self.texsize.y - self.keysize.y

        # update display list
        self._current_cache['usedlabel'] = []
        with self._current_cache[mode]:

            # draw lines
            for index in xrange(1, ky + 1):
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
                            font_size = int(14 * s)
                            if font_size < 8:
                                font_size = 8
                            color = self.style['color']
                            if internal_action is not None:
                                color = self.style['color-syskey']
                            drawLabel(label=displayed_str,
                                    pos=(x + kw / 2., y + self.keysize.y / 2.),
                                    font_size=font_size, bold=False,
                                    font_name=self.style.get('font-name'),
                                    color=color)
                            self._current_cache['usedlabel'].append(getLastLabel())
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
        self._lazy_update()

    def on_transform(self, *largs):
        # to lazy update only if scale change
        if self._old_scale != self.scale:
            self._old_scale = self.scale
            self._lazy_update()

    def on_layout_change(self, layout, *largs):
        self._layout_widget.visible = False
        self.layout = layout()
        self._need_update = 'now'

    def on_update(self):
        super(MTVKeyboard, self).on_update()
        self._update()

        if not len(self._last_key_down):
            return
        self._last_key_repeat_timeout -= getFrameDt()
        if self._last_key_repeat_timeout < 0:
            self._last_key_repeat -= getFrameDt()
            if self._last_key_repeat > 0:
                return
            self._last_key_repeat = self.repeat
            key = self._last_key_down[-1]
            self.dispatch_event('on_key_down', key, True)
            self.dispatch_event('on_key_up', key, True)


    def draw(self):
        # background
        set_color(*self.style['bg-color'])
        drawCSSRectangle(size=self.size, style=self.style)

        # content dynamic update
        with gx_matrix:
            glTranslatef(self.style['margin'][3], self.style['margin'][2], 0)

            # draw precalculated background
            self._current_cache['background'].draw()

            # draw active keys layer
            # +2 and -4 result of hard margin coded in _do_update (m = 3 * s)
            # we substract 1 cause of border (draw-border is activated.)
            set_color(*self.style['color-down'])
            for key, size in self._active_keys:
                x, y, w, h = size
                drawCSSRectangle(pos=(x+2, y+2), size=(w-4, h-4),
                    style=self.style, prefix='key', state='down')

            # search the good scale for current precalculated keys layer
            if self._last_update_scale == self.scale:
                s = 1. / self.scale# / self._last_update_scale
                glScalef(s, s, s)
            else:
                s = 1. / self._last_update_scale
                glScalef(s, s, s)
            self._current_cache['keys'].draw()

    def get_key_at_pos(self, x, y):
        '''Return the key + size info on the current layout, at the coordinate (x, y)'''
        mtop, mright, mbottom, mleft = self.style['margin']
        w, h = self.width - mleft - mright, self.height - mtop - mbottom
        kx, ky = self.layout.SIZE
        keysize = Vector(w / kx, h / ky)
        if x < mleft or x > self.width - mright or \
           y < mbottom or y > self.height - mtop:
            return None
        index = ky-int((y - mbottom) /
                (self.height - mtop - mbottom)
                * ky)
        line = self.layout.__getattribute__('%s_%d' % (self.mode, index))
        x -= mleft
        kx = 0
        for key in line:
            kw = keysize.x * key[3]
            if x >= kx and x < kx + kw:
                h = (self.height - mtop - mbottom) / ky
                return (key, (kx, h * (ky-index), kw, h))
            kx += kw
        return None

    def on_key_down(self, key, repeat=False):
        if repeat is False:
            self._last_key_down.append(key)
            self._last_key_repeat_timeout = self.repeat_timeout
            self._last_key_repeat = self.repeat
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            if internal_str is not None:
                self.text += internal_str
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
            self.text = self.text[:-1]

    def on_key_up(self, key, repeat=False):
        if key in self._last_key_down and repeat is False:
            self._last_key_down.remove(key)
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
            x, y = self.to_local(touch.x, touch.y)
            keyinfo = self.get_key_at_pos(x, y)
            if keyinfo is not None:
                key, size = keyinfo
                if key not in self._active_keys:
                    touch.userdata['vkeyboard_key'] = keyinfo
                    self._active_keys.append(keyinfo)
                    self.dispatch_event('on_key_down', key)
                return True
        return super(MTVKeyboard, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if 'vkeyboard_key' in touch.userdata:
            keyinfo = touch.userdata['vkeyboard_key']
            key, size = keyinfo
            if keyinfo in self._active_keys:
                self._active_keys.remove(keyinfo)
            self.dispatch_event('on_key_up', key)
            return True
        return super(MTVKeyboard, self).on_touch_up(touch)


# Register layouts
# Don't go further if we generate documentation
if not 'PYMT_DOC' in os.environ:
    MTVKeyboard.add_custom_layout(KeyboardLayoutQWERTY)
    MTVKeyboard.add_custom_layout(KeyboardLayoutAZERTY)
