'''
TextArea: a multiline text input, based on TextInput

TextArea keystrokes :
    * shift + cursor movement: activate selection
    * ctrl + c: copy current selection into clipboard
    * ctrl + x: cut current selection into clipboard
    * ctrl + v: paste current clipboard text
    * ctrl + a: select all the text
'''

__all__ = ('MTTextArea', )

import re
from pymt.cache import Cache
from pymt.graphx import set_color, drawLine
from pymt.base import getFrameDt, getWindow
from pymt.graphx import drawRectangle
from pymt.core.text import Label
from pymt.core.clipboard import Clipboard
from pymt.utils import boundary
from pymt.ui.widgets.composed.textinput import MTTextInput

FL_IS_NEWLINE = 0x01

# add a cache, really not sure about the usage right now.
Cache.register('textarea.label', timeout=60.)

class MTTextArea(MTTextInput):
    '''A multi line text input widget

    :Parameters:
        `tab_width`: int, default to 4
            Indicate how much space should take a tabulation. 1 = size of one
            space.
    '''
    def __init__(self, **kwargs):
        self._glyph_size = {}
        self._scroll_x = 0
        self._scroll_y = 5
        self._selection = False
        self._selection_text = ''
        self._selection_from = None
        self._selection_to = None
        super(MTTextArea, self).__init__(**kwargs)

        self.tab_width = kwargs.get('tab_width', 4)


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

        self.cursor_row = 0
        self.cursor_col = 0
        self.lines = []
        self.lines_flags = []
        self.value = kwargs.get('label') or ''
        self.buffer_size = kwargs.get('buffer_size') or 128000

    def _recalc_size(self):
        # We could do this as .size property I suppose, but then we'd
        # be calculating it all the time when .size is accessed.
        num = len(self.lines)
        if not num:
            return
        # The following two if statements ensure that the textarea remains
        # easily clickable even if there's no content.
        if self.autosize or self.autoheight:
            self.height = num * self.line_height + self.line_spacing * (num - 1)
        if (self.autosize or self.autowidth):
            self.width = max(label.content_width for label in self.line_labels)

    def _get_value(self):
        lf = self.lines_flags
        l = self.lines
        # raw version
        # out = []
        # for idx, elem in enumerate(l):
        #    if lf[idx] & FL_IS_NEWLINE:
        #        out.append('\n')
        #    out.append(elem)
        # return ''.join(out)
        # optimized version
        return ''.join([('\n' if (lf[i] & FL_IS_NEWLINE) else '') + l[i] \
                        for i in range(len(l))])
    def _set_value(self, text):
        old_value = self.value
        self._refresh_lines(text)
        self.cursor = self.get_cursor_from_index(len(text))
        self.cursor_fade = 0
        self._init_glyph_sizes()
        self._recalc_size()
        if old_value != self.value:
            self.dispatch_event('on_text_change', self)
    value = property(_get_value, _set_value)

    def _get_cursor(self):
        return self.cursor_col, self.cursor_row
    def _set_cursor(self, pos):
        l = self.lines
        cc, cr = pos
        self.cursor_row = cr = boundary(0, len(l) - 1, cr)
        self.cursor_col = boundary(0, len(l[cr]), cc)
        self.cursor_fade = 1
    cursor = property(_get_cursor, _set_cursor,
                      '''Get/set the (col,row) of the cursor''')

    def _refresh_lines(self, text=None):
        '''Recreate all lines / flags / labels from current value
        '''
        cursor_index = self.cursor_index
        text = text if type(text) in (str, str) else self.value
        self.lines, self.lines_flags = self._split_smart(text)
        self.line_labels = list(map(self.create_line_label, self.lines))
        self.line_height = self.line_labels[0].content_height
        self.line_spacing = 2
        self._recalc_size()
        # now, if the text change, maybe the cursor is not as the same place as
        # before. so, try to set the cursor on the good place
        self.cursor = self.get_cursor_from_index(cursor_index)

    def _tokenize(self, text):
        '''Tokenize a text string from some delimiters
        '''
        delimiters = ' ,\'".;:\n\r\t'
        oldindex = 0
        for index, char in enumerate(text):
            if char not in delimiters:
                continue
            if oldindex != index:
                yield text[oldindex:index]
            yield text[index:index+1]
            oldindex = index+1
        yield text[oldindex:]

    def _split_smart(self, text):
        '''Do a "smart" split. If autowidth or autosize is set,
        we are not doing smart split, just a split on line break.
        Otherwise, we are trying to split as soon as possible, to prevent
        overflow on the widget.
        '''
        # depend of the options, split the text on line, or word
        if self.autowidth or self.autosize:
            lines = text.split('\n')
            lines_flags = [0] + [FL_IS_NEWLINE] * (len(lines) - 1)
            return lines, lines_flags

        # no autosize, do wordwrap.
        x = flags = 0
        line = []
        lines = []
        lines_flags = []
        width = self.width - self.__padding_x * 2
        glyph_size = self.glyph_size

        # try to add each word on current line.
        for word in self._tokenize(text):
            is_newline = (word == '\n')
            w = glyph_size(word)
            # if we have more than the width, or if it's a newline,
            # push the current line, and create a new one
            if (x + w > width and line) or is_newline:
                lines.append(''.join(line))
                lines_flags.append(flags)
                flags = 0
                line = []
                x = 0
            if is_newline:
                flags |= FL_IS_NEWLINE
            else:
                x += w
                line.append(word)
        if line or flags & FL_IS_NEWLINE:
            lines.append(''.join(line))
            lines_flags.append(flags)

        return lines, lines_flags

    #
    # Selection control
    #

    def cancel_selection(self):
        '''Cancel current selection if any
        '''
        self._selection = False
        self._selection_finished = True

    def delete_selection(self):
        '''Suppress from the value current selection if any
        '''
        if not self._selection:
            return
        v = self.value
        text = v[:self._selection_from] + v[self._selection_to:]
        self.value = text
        self.cursor = self.get_cursor_from_index(self._selection_from)
        self.cancel_selection()

    def _update_selection(self, finished=False):
        '''Update selection text and order of from/to if finished is True.
        Can be call multiple time until finished=True.
        '''
        a, b = self._selection_from, self._selection_to
        if a > b:
            a, b = b, a
        self._selection_finished = finished
        self._selection_text = self.value[a:b]
        if not finished:
            self._selection = True
        else:
            self._selection_from = a
            self._selection_to = b
            self._selection = bool(len(self._selection_text))

    def _delete_line(self, idx):
        '''Delete current line, and fix cursor position
        '''
        assert(idx < len(self.lines))
        self.lines.pop(idx)
        self.lines_flags.pop(idx)
        self.line_labels.pop(idx)
        self.cursor = self.cursor

    def _set_line_text(self, line_num, text):
        '''Set current line with other text than the default one.
        '''
        self.lines[line_num] = text
        self.line_labels[line_num] = self.create_line_label(text)

    def get_line_options(self):
        '''Get or create line options, to be used for Label creation
        '''
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
        '''Create a label from a text, using line options
        '''
        ntext = text.replace('\n', '').replace('\t', ' ' * self.tab_width)
        kw = self.get_line_options()
        cid = '%s\0%s' % (ntext, str(kw))
        label = Cache.get('textarea.label', cid)
        if not label:
            label = Label(ntext, **kw)
            Cache.append('textarea.label', cid, label)
        return label

    def glyph_size(self, g):
        '''Get or add size of a glyph
        '''
        if g not in self._glyph_size:
            l = self.create_line_label(g)
            self._glyph_size[g] = l.content_width
        return self._glyph_size[g]

    def _init_glyph_sizes(self):
        '''First populate of glyph table
        '''
        # populating glyphs sizes
        for line in self.lines:
            for g in line:
                self.glyph_size(g)

    def line_at_pos(self, pos):
        '''Return the line from the current touch position
        '''
        line = int(((self.y+self.height)-pos[1])/(self.line_height+self.line_spacing))
        return max(0, min(line, len(self.lines)-1))

    def place_cursor(self, pos):
        '''Place the cursor near the touch position
        '''
        self.cursor_fade = 1
        self.cursor_row = self.line_at_pos(pos)
        text = self.lines[self.cursor_row]
        offset = 0
        cursor = 0
        while offset < (pos[0]-self.x) and cursor < len(text):
            offset += self.glyph_size(text[cursor])
            cursor += 1
        self.cursor_col = cursor

    @property
    def cursor_index(self):
        '''Return the cursor index in the text/value.
        '''
        l = self.lines
        if len(l) == 0:
            return 0
        lf = self.lines_flags
        index, cr = self.cursor
        for row in range(cr):
            index += len(l[row])
            if lf[row] & FL_IS_NEWLINE:
                index += 1
        if lf[cr] & FL_IS_NEWLINE:
            index += 1
        return index

    def cursor_offset(self):
        '''Get the cursor x offset on the current line
        '''
        offset = 0
        for i in range(self.cursor_col):
            offset += self.glyph_size(self.lines[self.cursor_row][i])
        return offset

    def get_cursor_from_index(self, index):
        '''Return the (row, col) of the cursor from text index'''
        index = boundary(0, len(self.value), index)
        if index <= 0:
            return 0, 0
        lf = self.lines_flags
        l = self.lines
        i = 0
        for row in range(len(l)):
            ni = i + len(l[row])
            if lf[row] & FL_IS_NEWLINE:
                ni += 1
                i += 1
            if ni >= index:
                return index - i, row
            i = ni
        return index, row

    def draw_cursor(self, x, y):
        '''Draw the cursor on the widget
        '''
        if not int(self.cursor_fade):
            return
        set_color(*self.style.get('cursor-color'))
        drawRectangle(size=(2, -self.line_height),
                      pos=(x + self.cursor_offset() - self._scroll_x, y))

    def draw_label(self):
        '''Draw the label on the widget, with taking care of scroll view and
        selection
        '''
        cursor_row = self.cursor_row
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
        if cursor_row < max_lines_displayed / 2:
            self._scroll_y = 0
        elif cursor_row > len(self.lines) - max_lines_displayed / 2:
            self._scroll_y = int(len(self.lines) - max_lines_displayed)
        else:
            self._scroll_y = int(cursor_row - max_lines_displayed / 2)

        # selection
        selection_active = self._selection

        # draw labels
        labels = self.line_labels
        is_active_input = self.is_active_input
        x = self.x + self.__padding_x
        y = self.top - self.__padding_y + (self._scroll_y * dy)
        miny = self.y + self.__padding_y
        maxy = self.top - self.__padding_y
        draw_selection = self.draw_selection
        for line_num, value in enumerate(self.lines):
            if miny <= y <= maxy:
                label = labels[line_num]
                label.viewport_pos = sx, 0
                label.pos = x, y
                if selection_active:
                    draw_selection(label, line_num)
                label.draw()
                if cursor_row == line_num and is_active_input:
                    self.draw_cursor(x, y)
            y -= dy

    def draw_selection(self, label, line_num):
        '''Draw the current selection on the widget.
        '''
        a, b = self._selection_from, self._selection_to
        if a > b:
            a, b = b, a
        s1c, s1r = self.get_cursor_from_index(a)
        s2c, s2r = self.get_cursor_from_index(b)
        if line_num < s1r or line_num > s2r:
            return
        x1 = label.x
        x2 = label.x + label.width
        y1 = label.y - self.line_height
        g = self.glyph_size
        if line_num == s1r:
            lines = self.lines[line_num]
            x1 += sum([g(x) for x in lines[:s1c]])
        if line_num == s2r:
            lines = self.lines[line_num]
            x2 = label.x + sum([g(x) for x in lines[:s2c]])
        set_color(*self.style.get('selection-color'))
        drawRectangle(pos=(x1, y1), size=(x2-x1, self.line_height))


    def on_update(self):
        super(MTTextArea, self).on_update()
        self.cursor_fade = (self.cursor_fade + getFrameDt() * 2) % 2

    def on_press(self, touch):
        if not self.is_active_input:
            self.show_keyboard()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.place_cursor((touch.x - self.__padding_x,
                               touch.y + self.__padding_y))
            touch.userdata['%scursor' % self.id] = True
            self._selection_from = self.cursor_index
        return super(MTTextArea, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.userdata.get('%scursor' % self.id) and \
           touch.grab_current == self:
            self.place_cursor((touch.x - self.__padding_x,
                               touch.y + self.__padding_y))
            self._selection_to = self.cursor_index
            self._update_selection()
        return super(MTTextArea, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.userdata.get('%scursor' % self.id) and \
           touch.grab_current == self:
            self.place_cursor((touch.x - self.__padding_x,
                               touch.y + self.__padding_y))
            self._selection_to = self.cursor_index
            self._update_selection(True)
        self._can_deactive = False
        if super(MTTextArea, self).on_touch_up(touch):
            return True

    def _kbd_on_text_change(self, value):
        pass

    def insert_text(self, c):
        '''Insert new text on the current cursor position
        '''
        if len(self.value) >= self.buffer_size:
            return
        cc, cr = self.cursor
        ci = self.cursor_index
        text = self.lines[cr]
        new_text = text[:cc] + c + text[cc:]
        self._set_line_text(cr, new_text)
        self._refresh_lines()
        self.cursor = self.get_cursor_from_index(ci + len(c))
        self.dispatch_event('on_text_change', self)

    def do_backspace(self):
        '''Do backspace operation from the current cursor position
        '''
        cc, cr = self.cursor
        text = self.lines[cr]
        cursor_index = self.cursor_index
        if cc == 0 and cr == 0:
            return
        if cc == 0:
            text_last_line = self.lines[cr - 1]
            self._set_line_text(cr - 1, text_last_line + text)
            self._delete_line(cr)
        else:
            ch = text[cc-1]
            new_text = text[:cc-1] + text[cc:]
            self._set_line_text(cr, new_text)

        self._refresh_lines()
        self.cursor = self.get_cursor_from_index(cursor_index - 1)
        self.dispatch_event('on_text_change', self)

    def do_cursor_movement(self, action):
        '''Do a cursor movement
        (cursor_{left,right,up,down,home,end,pgup,pgdown})
        from the current cursor position
        '''
        pgmove_speed = 3
        if action == 'cursor_up':
            self.cursor_row = max(self.cursor_row - 1, 0)
            self.cursor_col = min(len(self.lines[self.cursor_row]), self.cursor_col)
        elif action == 'cursor_down':
            self.cursor_row = min(self.cursor_row + 1, len(self.lines) - 1)
            self.cursor_col = min(len(self.lines[self.cursor_row]), self.cursor_col)
        elif action == 'cursor_left':
            self.cursor = self.get_cursor_from_index(self.cursor_index - 1)
        elif action == 'cursor_right':
            self.cursor = self.get_cursor_from_index(self.cursor_index + 1)
        elif action == 'cursor_home':
            self.cursor_col = 0
        elif action == 'cursor_end':
            self.cursor_col = len(self.lines[self.cursor_row])
        elif action == 'cursor_pgup':
            self.cursor_row /= pgmove_speed
            self.cursor_col = min(len(self.lines[self.cursor_row]), self.cursor_col)
        elif action == 'cursor_pgdown':
            self.cursor_row = min((self.cursor_row + 1) * pgmove_speed, len(self.lines) - 1)
            self.cursor_col = min(len(self.lines[self.cursor_row]), self.cursor_col)

    def _kbd_on_key_down(self, key, repeat=False):
        self.cursor_fade = 1
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            if self._selection:
                self.delete_selection()
            self.insert_text(displayed_str)
        elif internal_action in ('shift', 'shift_L', 'shift_R'):
            self._selection_from = self._selection_to = self.cursor_index
            self._selection = True
            self._selection_finished = False
        elif internal_action.startswith('cursor_'):
            self.do_cursor_movement(internal_action)
            if self._selection and not self._selection_finished:
                self._selection_to = self.cursor_index
                self._update_selection()
            else:
                self.cancel_selection()
        elif self._selection and internal_action in ('del', 'backspace'):
            self.delete_selection()
        elif internal_action == 'del':
            # do backspace only if we have data after our cursor
            cursor = self.cursor
            self.do_cursor_movement('cursor_right')
            if cursor != self.cursor:
                self.do_backspace()
        elif internal_action == 'backspace':
            self.do_backspace()
        elif internal_action == 'enter':
            self.insert_text('\n')
        elif internal_action == 'escape':
            self.hide_keyboard()
        if internal_action != 'escape':
            self._recalc_size()

    def _kbd_on_key_up(self, key, repeat=False):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action in ('shift', 'shift_L', 'shift_R'):
            self._update_selection(True)

    def _window_on_key_down(self, key, scancode=None, str=None):
        if str and not key in list(self.interesting_keys.keys()) + [27]:
            modifiers = getWindow().modifiers
            if 'ctrl' in modifiers:
                if key == ord('x'): # cut selection
                    Clipboard.put(self._selection_text, 'text/plain')
                    self.delete_selection()
                elif key == ord('c'): # copy selection
                    Clipboard.put(self._selection_text, 'text/plain')
                elif key == ord('v'): # paste selection
                    data = Clipboard.get('text/plain')
                    if data:
                        self.delete_selection()
                        self.insert_text(data)
                elif key == ord('a'): # select all
                    self._selection_from = 0
                    self._selection_to = len(self.value)
                    self._update_selection(True)
            else:
                if self._selection:
                    self.delete_selection()
                self.insert_text(str)
            self._recalc_size()
        return super(MTTextArea, self)._window_on_key_down(key, scancode, str)
