'''
TextArea: a multiline text input, based on TextInput
'''

__all__ = ('MTTextArea', )

import re
from pymt.graphx import set_color
from pymt.base import getFrameDt
from pymt.graphx import drawRectangle
from pymt.core.text import Label
from pymt.ui.widgets.composed.textinput import MTTextInput

class MTTextArea(MTTextInput):
    '''A multi line text input widget'''
    def __init__(self, **kwargs):
        self._glyph_size = {}
        self._scroll_x = 0
        self._scroll_y = 5
        super(MTTextArea, self).__init__(**kwargs)

        padding = kwargs.get('padding', None)
        padding_x = kwargs.get('padding_x', None)
        padding_y = kwargs.get('padding_y', None)
        if not padding_x:
            if type(padding) in (tuple, list):
                padding_x = float(padding[0])
            elif padding is not None:
                padding_x = float(padding)
            else:
                padding_x = 0
        if not padding_y:
            if type(padding) in (tuple, list):
                padding_y = float(padding[1])
            elif padding is not None:
                padding_y = float(padding)
            else:
                padding_y = 0
        self.__padding_x = padding_x
        self.__padding_y = padding_y

        self.value = kwargs.get('label') or ''
        self.buffer_size = kwargs.get('buffer_size') or 128000

    def _recalc_size(self):
        # We could do this as .size property I suppose, but then we'd
        # be calculating it all the time when .size is accessed.
        num = len(self.lines)
        # The following two if statements ensure that the textarea remains
        # easily clickable even if there's no content.
        if num:
            if self.autosize or self.autoheight:
                self.height = num * self.line_height + self.line_spacing * (num - 1)
            if (self.autosize or self.autowidth):
                self.width = max(label.content_width for label in self.line_labels)

    def _get_value(self):
        try:
            return ''.join(self.lines)
        except AttributeError:
            return ''
    def _set_value(self, text):
        old_value = self.value
        self._refresh_lines(text)
        self.edit_line = len(self.lines)-1 #line being edited
        self.cursor = 1 #pos inside line
        self.cursor_fade = 0
        self.init_glyph_sizes()
        self._recalc_size()
        if old_value != self.value:
            self.dispatch_event('on_text_change', self)
    value = property(_get_value, _set_value)

    def _refresh_lines(self, text=None):
        text = text or self.value
        self.lines = self._split_smart(text)
        self.line_labels = map(self.create_line_label, self.lines)
        self.line_height = self.line_labels[0].content_height
        self.line_spacing = 2
        self._recalc_size()

    def _tokenize(self, text):
        delimiters = ' ,\'".;:\n\r\t'
        oldindex = 0
        for index, char in enumerate(text):
            if char not in delimiters:
                continue
            yield text[oldindex:index]
            yield text[index:index+1]
            oldindex = index+1
        yield text[oldindex:]

    def _split_smart(self, text):
        # depend of the options, split the text on line, or word
        if self.autowidth or self.autosize:
            return text.split('\n')

        # no autosize, do wordwrap.
        x = 0
        line = []
        lines = []
        width = self.width
        glyph_size = self.glyph_size

        # try to add each word on current line.
        for word in self._tokenize(text):
            is_newline = word == '\n'
            w = glyph_size(word)
            # if we have more than the width, or if it's a newline,
            # push the current line, and create a new one
            if (x + w > width and line) or is_newline:
                lines.append(''.join(line))
                line = []
                x = 0
            x += w
            line.append(word)
        if line:
            lines.append(''.join(line))

        return lines

    def set_line_text(self, line_num, text):
        self.lines[line_num] = text
        self.line_labels[line_num].label = text

    def get_line_options(self):
        if not hasattr(self, '__line_options'):
            kw = self.__line_options = self.kwargs.copy()
            # Honour attributes like color.
            # XXX Currently only works once initially. Not updated if self.color is changed!
            #     What would be a proper solution?
            kw['anchor_x'] = 'left'
            kw['anchor_y'] = 'top'
            # force padding to 0, otherwise, the content width will take padding in
            # account, and the cursor display will be completly messed up
            # FIXME: handle padding ourself !
            kw['padding_x'] = 0
            kw['padding_y'] = 0
            kw['padding'] = (0, 0)
            w, h = self.size
            w -= self.__padding_x * 2
            h -= self.__padding_y * 2
            kw['viewport_size'] = (w, h)
        return self.__line_options

    def create_line_label(self, text):
        kw = self.get_line_options()
        label = Label(text.replace('\n', ''), **kw)
        return label

    def glyph_size(self, g):
        if not self._glyph_size.has_key(g):
            l = self.create_line_label(g)
            self._glyph_size[g] = l.content_width
        return self._glyph_size[g]

    def init_glyph_sizes(self):
        # populating glyphs sizes
        for line in self.lines:
            for g in line:
                self.glyph_size(g)

    def line_at_pos(self, pos):
        line = int(((self.y+self.height)-pos[1])/(self.line_height+self.line_spacing))
        return max(0, min(line, len(self.lines)-1))

    def place_cursor(self, pos):
        self.edit_line = self.line_at_pos(pos)
        text = self.lines[self.edit_line]
        offset = 0
        cursor = 0
        while offset < (pos[0]-self.x) and cursor < len(text):
            offset += self.glyph_size(text[cursor])
            cursor += 1
        self.cursor = cursor

    def cursor_offset(self):
        offset = 0
        for i in xrange(self.cursor):
            try:
                offset += self.glyph_size(self.lines[self.edit_line][i])
            except IndexError:
                pass
        return offset

    def draw_cursor(self, x, y):
        set_color(1, 0, 0, int(self.cursor_fade))
        drawRectangle(size=(2, -self.line_height),
                      pos=(x + self.cursor_offset() - self._scroll_x, y))

    def draw_label(self):
        edit_line = self.edit_line
        offset = self.cursor_offset()
        dy = self.line_height + self.line_spacing

        # adjust view if the cursor is going outside the bounds
        self._scroll_x = 0
        if offset > self.width - self.__padding_x * 2:
            self._scroll_x = offset - self.width + self.__padding_x * 2
        sx = self._scroll_x

        # do the same for Y
        # this algo try to center the cursor as much as possible
        max_lines_displayed = (self.height - 2 * self.__padding_y) / dy
        max_lines_displayed = max(1, max_lines_displayed)
        if edit_line < max_lines_displayed / 2:
            self._scroll_y = 0
        elif edit_line > len(self.lines) - max_lines_displayed / 2:
            self._scroll_y = int(len(self.lines) - max_lines_displayed)
        else:
            self._scroll_y = int(edit_line - max_lines_displayed / 2)

        # draw labels
        labels = self.line_labels
        is_active_input = self.is_active_input
        x = self.x + self.__padding_x
        y = self.top - self.__padding_y + (self._scroll_y * dy)
        miny = self.y + self.__padding_y
        maxy = self.top - self.__padding_y
        for line_num, value in enumerate(self.lines):
            if miny <= y <= maxy:
                label = labels[line_num]
                label.viewport_pos = sx, 0
                label.pos = x, y
                label.draw()
                if edit_line == line_num and is_active_input:
                    self.draw_cursor(x, y)
            y -= dy

    def on_update(self):
        super(MTTextArea, self).on_update()
        self.cursor_fade = (self.cursor_fade+getFrameDt()*2)%2

    def on_press(self, touch):
        if not self.is_active_input:
            self.show_keyboard()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.place_cursor(touch.pos)
            touch.userdata[str(self.id)+'cursor'] = True
        return super(MTTextArea, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.userdata.get(str(self.id)+'cursor'):
            self.place_cursor(touch.pos)
        return super(MTTextArea, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        self._can_deactive = False
        if super(MTTextArea, self).on_touch_up(touch):
            return True

    def _kbd_on_text_change(self, value):
        pass

    def insert_character(self, c):
        ##print '>> insert_character()', self.cursor, self.edit_line, c
        if len(self.value) >= self.buffer_size:
            return
        text = self.lines[self.edit_line]
        new_text = text[:self.cursor] + c + text[self.cursor:]
        self.set_line_text(self.edit_line, new_text)
        self._refresh_lines()
        self.cursor += 1
        ##print self.cursor, self.edit_line, self.lines
        if self.lines[self.edit_line] == text:
            self.cursor = 1
            self.edit_line += 1
        self.dispatch_event('on_text_change', self)

    def do_backspace(self):
        ##print '>> do_backspace()', self.cursor, self.edit_line, self.lines
        if self.cursor == 0:
            ##print 'call case 0'
            if self.edit_line == 0:
                return #nothign to do, we all teh way at the top
            text_last_line = self.lines[self.edit_line-1]
            text = self.lines[self.edit_line]
            self.set_line_text(self.edit_line-1, text_last_line+text)
            self.lines.pop(self.edit_line)
            self.line_labels.pop(self.edit_line)
            self.edit_line -= 1
            self.cursor = len(text_last_line)
        else:
            text = self.lines[self.edit_line]
            if len(text) == 0:
                return
            ch = text[self.cursor-1]
            new_text = text[:self.cursor-1] + text[self.cursor:]
            self.set_line_text(self.edit_line, new_text)
            if ch == '\n':
                self.edit_line = max(0, self.edit_line - 1)
                self.cursor = len(self.lines[self.edit_line])
            else:
                self.cursor -= 1

        self._refresh_lines()
        ##print '<< do_backspace()', self.cursor, self.edit_line, self.lines
        self.dispatch_event('on_text_change', self)

    def do_cursor_movement(self, action):
        pgmove_speed = 3
        if action == 'cursor_up':
            self.edit_line = max(self.edit_line - 1, 0)
            self.cursor = min(len(self.lines[self.edit_line]), self.cursor)
        elif action == 'cursor_down':
            self.edit_line = min(self.edit_line + 1, len(self.lines) - 1)
            self.cursor = min(len(self.lines[self.edit_line]), self.cursor)
        elif action == 'cursor_left':
            self.cursor = max(self.cursor - 1, 0)
        elif action == 'cursor_right':
            self.cursor = min(self.cursor + 1, len(self.lines[self.edit_line]))
        elif action == 'cursor_home':
            self.cursor = 0
        elif action == 'cursor_end':
            self.cursor = len(self.lines[self.edit_line])
        elif action == 'cursor_pgup':
            self.edit_line /= pgmove_speed
            self.cursor = min(len(self.lines[self.edit_line]), self.cursor)
        elif action == 'cursor_pgdown':
            self.edit_line = min((self.edit_line + 1) * pgmove_speed, len(self.lines) - 1)
            self.cursor = min(len(self.lines[self.edit_line]), self.cursor)

    def _kbd_on_key_up(self, key, repeat=False):
        self.cursor_fade = 1
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            self.insert_character(displayed_str)
        elif internal_action.startswith('cursor_'):
            self.do_cursor_movement(internal_action)
        elif internal_action == 'del':
            pass
        elif internal_action == 'backspace':
            self.do_backspace()
        elif internal_action == 'enter':
            self.insert_character('\n')
        elif internal_action == 'escape':
            self.hide_keyboard()
        if internal_action != 'escape':
            self._recalc_size()

    def _window_on_key_down(self, key, scancode=None, unicode=None):
        if unicode and not key in self.interesting_keys.keys() + [9, 27]:
            self.insert_character(unicode)
            self._recalc_size()
        return super(MTTextArea, self)._window_on_key_down(key, scancode, unicode)
