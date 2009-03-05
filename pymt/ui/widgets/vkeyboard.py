from __future__ import with_statement
__all__ = ['MTTextInput', 'MTVKeyboard', 'MTKeyButton']

from pyglet.text import Label
from pyglet.window import key
from ...graphx import set_color, drawRectangle, drawRoundedRectangle, DO, gx_blending, GlDisplayList
from ..factory import MTWidgetFactory
from button import MTButton
from scatter import MTScatterWidget
from layout.boxlayout import MTBoxLayout


class MTTextInput(MTButton):
    '''
    A text input widget is a simple label widget that will pop up a virtual keyboard when touched
    any input of the virtual keyboard will then have effect on the TextInput widget
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('font_bold', True)
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        super(MTTextInput, self).__init__(**kwargs)
        self._keyboard = None
        self.original_width = self.width
        self.is_active_input = False
        self.added_keyboard = False
        self.padding = 20

        self.register_event_type('on_text_change')
        self.register_event_type('on_text_validate')

    def _get_keyboard(self):
        if not self._keyboard:
            self._keyboard = MTVKeyboard(self)
        return self._keyboard
    keyboard = property(_get_keyboard)

    def on_release(self,touchID, x, y):
        if self.is_active_input:
            self.hide_keyboard()
        else:
            self.show_keyboard()

    def reposition(self):
        self.label_obj.text = self.label
        self.label_obj.x = self.x + self.padding
        self.label_obj.y = self.y
        self.width =  self.label_obj.content_width + self.padding * 2
        if self.width < self.original_width:
            self.width = self.original_width

    def on_move(self, w, h):
        self.reposition()

    def on_text_change(self):
        self.reposition()

    def on_text_validate(self):
        pass

    def show_keyboard(self):
        self.get_parent_window().add_widget(self.keyboard)
        self.get_parent_window().add_on_key_press(self.on_key_press)
        self.get_parent_window().add_on_text(self.on_text)
        self.is_active_input = True

    def hide_keyboard(self):
        self.get_parent_window().remove_widget(self.keyboard)
        self.get_parent_window().remove_on_key_press(self.on_key_press)
        self.get_parent_window().remove_on_text(self.on_text)
        self.is_active_input = False

    def draw(self):
        if self.state[0] == 'down':
            set_color(0.5,0.5,0.5,0.5)
            drawRectangle((self.x,self.y) , (self.width, self.height))
        else:
            set_color(*self.bgcolor)
            drawRectangle((self.x,self.y) , (self.width, self.height))
        self.label_obj.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.hide_keyboard()
            return True
        elif symbol == key.BACKSPACE:
            self.keyboard.on_key_up(MTVKeyboard.KEY_BACKSPACE)
        elif symbol == key.ENTER:
            self.keyboard.on_key_up(MTVKeyboard.KEY_ENTER)

    def on_text(self, text):
        self.keyboard.text_widget.label = self.keyboard.text_widget.label + text
        self.reposition()


class MTKeyButton(MTButton):
    '''Internal Class used in MTVKeyboard'''
    def __init__(self, keyboard, **kwargs):
        super(MTKeyButton, self).__init__(**kwargs)
        self.keyboard = keyboard

    def on_press(self, touchID, x, y):
        self.keyboard.on_key_down(self.label)
        self.keyboard.active_keys[self] = self

    def on_release(self, touchID, x, y):
        if self.keyboard.active_keys.has_key(self):
            del self.keyboard.active_keys[self]
            self.keyboard.on_key_up(self.label)


class MTVKeyboard(MTScatterWidget):
    '''A virtual keyboard that can be scaled/rotate/moved'''

    KEY_SPACE       = 'Space'
    KEY_ESCAPE      = 'Esc'
    KEY_BACKSPACE   = '<-'
    KEY_SHIFT       = 'Shift'
    KEY_CAPSLOCK    = 'CL'
    KEY_ENTER       = 'Enter'

    _row_keys       = ['1234567890-=', 'qwertyuiop', 'asdfghjkl;', 'zxcvbnm,./']
    _row_keyscaps   = ['!@#$%^&*()_+', 'QWERTYUIOP', 'ASDFGHJKL:', 'ZXCVBNM<>?']

    def __init__(self, text_widget, pos=(0,0)):
        MTScatterWidget.__init__(self, pos=(0,0), size=(400,200))

        # setup caps keys
        self.add_widget(self._setup_keys(MTVKeyboard._row_keyscaps), side='back')
        # setup normal keys
        self.add_widget(self._setup_keys(MTVKeyboard._row_keys), side='front')

        self.dlfront        = GlDisplayList()
        self.dlback         = GlDisplayList()
        self.active_keys    = {}
        self.text_widget    = text_widget
        self.draw_children  = False
        self.is_shift       = False
        self.is_capslock    = False

    def do_flip_caps(self):
        caps = self.is_capslock
        if self.is_shift:
            caps = not caps
        if caps:
            if self.side == 'front':
                self.flip()
        elif self.side == 'back':
            self.flip()

    def on_key_down(self, k_str):
        if k_str == MTVKeyboard.KEY_SHIFT:
            self.is_shift = True
            self.do_flip_caps()
            return True

    def on_key_up(self, k_str):
        if k_str == MTVKeyboard.KEY_ENTER:
            self.text_widget.dispatch_event('on_text_validate')
            self.text_widget.hide_keyboard()
            return True

        elif k_str == MTVKeyboard.KEY_ESCAPE:
            self.text_widget.hide_keyboard()
            return True

        elif k_str == MTVKeyboard.KEY_BACKSPACE:
            self.text_widget.label = self.text_widget.label[:-1]

        elif k_str == MTVKeyboard.KEY_SPACE:
            self.text_widget.label += ' '

        elif k_str == MTVKeyboard.KEY_SHIFT:
            self.is_shift = False
            self.do_flip_caps()
            return True

        elif k_str == MTVKeyboard.KEY_CAPSLOCK:
            self.is_capslock = not self.is_capslock
            self.do_flip_caps()
            return True

        else:
            self.text_widget.label = self.text_widget.label + k_str

        self.text_widget.dispatch_event('on_text_change')
        return True

    def update_dl(self):
        with DO(self.dlfront, gx_blending):
            set_color(*self.bgcolor)
            drawRoundedRectangle((0,0), self.size)
            for w in self.children_front:
                w.dispatch_event('on_draw')
        with DO(self.dlback, gx_blending):
            set_color(*self.bgcolor)
            drawRoundedRectangle((0,0), self.size)
            for w in self.children_back:
                w.dispatch_event('on_draw')

    def _setup_keys(self, keys):
        k_width = 25
        spacing = 3
        padding = 30
        border_radius = 2

        vlayout = MTBoxLayout(orientation='vertical', pos=(padding,padding),
                              spacing=spacing, invert_y=True)
        key_options = {'border_radius': border_radius}

        for j in range(4):
            layout = MTBoxLayout(spacing=spacing)

            # special keys on left
            if j == 0:
                k_str   = MTVKeyboard.KEY_ESCAPE
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width, k_width), **key_options)
                layout.add_widget(k_btn)
            elif j == 1:
                k_str   = ''
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width*0.5, k_width), **key_options)
                layout.add_widget(k_btn)
            elif j == 2:
                k_str   = MTVKeyboard.KEY_CAPSLOCK
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width, k_width), **key_options)
                layout.add_widget(k_btn)
            elif j == 3:
                k_str   = MTVKeyboard.KEY_SHIFT
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width*1.5, k_width), **key_options)
                layout.add_widget(k_btn)

            # regular keys
            num_keys = len(keys[j])
            for i in range(num_keys):
                k_str   = keys[j][i]
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width, k_width), **key_options)
                layout.add_widget(k_btn)

            # special keys on right
            if j == 1:
                k_str   = MTVKeyboard.KEY_BACKSPACE
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width*2.5 +3, k_width), **key_options)
                layout.add_widget(k_btn)
            elif j == 2:
                k_str   = MTVKeyboard.KEY_ENTER
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width*2+3, k_width), **key_options)
                layout.add_widget(k_btn)
            elif j == 3:
                k_str   = MTVKeyboard.KEY_SHIFT
                k_btn   = MTKeyButton(self, label=k_str, size=(k_width*1.5+3, k_width), **key_options)
                layout.add_widget(k_btn)

            vlayout.add_widget(layout)

        layout = MTBoxLayout(spacing=3)
        space_key = MTKeyButton(self, label=MTVKeyboard.KEY_SPACE, size=(361, k_width), **key_options)
        layout.add_widget(space_key)
        vlayout.add_widget(layout)
        self.size = (vlayout.content_width + padding * 2,
                     vlayout.content_height + padding * 2)
        return vlayout

    def draw_active_children(self):
        for key in self.active_keys:
            self.active_keys[key].draw()

    def draw(self):
        if not self.dlfront.is_compiled() or not self.dlback.is_compiled():
            self.update_dl()
        if self.side == 'front':
            self.dlfront.draw()
        else:
            self.dlback.draw()
        self.draw_active_children()

# Register all base widgets
MTWidgetFactory.register('MTTextInput', MTTextInput)
