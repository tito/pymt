'''
TextInput: a text input who instance vkeyboard if needed
'''

from ....graphx import set_color, drawCSSRectangle, drawLine, GlDisplayList
from ..button import MTButton
from ...factory import MTWidgetFactory
from vkeyboard import MTVKeyboard
from pyglet import window

class MTTextInput(MTButton):
    '''
    A text input widget is a simple label widget that will pop up
    a virtual keyboard when touched any input of the virtual keyboard
    will then have effect on the TextInput widget.

    :Events:
        `on_text_change` (text)
            Fired when the content of text input is changed
        `on_text_validate` ()
            Fired when the text is validate (when ENTER is hit on keyboard)
    '''
    def __init__(self, **kwargs):
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
            self._keyboard = MTVKeyboard()
            self._keyboard.push_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up
            )
        return self._keyboard
    keyboard = property(_get_keyboard)

    def on_press(self, touch):
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

    def _kbd_on_text_change(self, value):
        self.label = value
        self.reposition()
        self.dispatch_event('on_text_change', value)

    def _kbd_on_key_up(self, key):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            return
        elif internal_action == 'enter':
            self.hide_keyboard()
            self.dispatch_event('on_text_validate')
        elif internal_action == 'escape':
            self.hide_keyboard()

    def on_text_validate(self):
        pass

    def on_text_change(self, text):
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
        if self.is_active_input:
            set_color(*self.style.get('bg-color'))
            drawLine([self.center[0], self.center[1],
                      self.keyboard.center[0], self.keyboard.center[1]])
        if self.state[0] == 'down':
            set_color(0.5,0.5,0.5,0.5)
            drawCSSRectangle((self.x,self.y) , (self.width, self.height), style=self.style)
        else:
            set_color(*self.style.get('bg-color'))
            drawCSSRectangle((self.x,self.y) , (self.width, self.height), style=self.style)
        self.label_obj.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == window.key.ESCAPE:
            self.hide_keyboard()
            return True
        elif symbol == window.key.BACKSPACE:
            key = (None, None, 'backspace', 1)
            self.keyboard.on_key_down(key)
            self.keyboard.on_key_up(key)
        elif symbol in [window.key.ENTER, window.key.NUM_ENTER]:
            key = (None, None, 'enter', 1)
            self.keyboard.on_key_down(key)
            self.keyboard.on_key_up(key)

    def on_text(self, text):
        if text in ("\r", "\n"):
            self.on_key_press(window.key.ENTER, None)
        else:
            self.keyboard.text = self.keyboard.text + text

# Register all base widgets
MTWidgetFactory.register('MTTextInput', MTVKeyboard)
