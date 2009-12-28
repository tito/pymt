'''
TextInput: a text input who instance vkeyboard if needed
'''

__all__ = ['MTTextInput']

from ....graphx import set_color, drawCSSRectangle, drawLine, GlDisplayList
from ..button import MTButton
from ...factory import MTWidgetFactory
from vkeyboard import MTVKeyboard

class MTTextInput(MTButton):
    '''
    A text input widget is a simple label widget that will pop up
    a virtual keyboard when touched any input of the virtual keyboard
    will then have effect on the TextInput widget.

    :Parameters:
        `keyboard` : MTVkeyboard object, default to None
            Use another MTVKeyboard than the default one

    :Events:
        `on_text_change` (text)
            Fired when the content of text input is changed
        `on_text_validate` ()
            Fired when the text is validate (when ENTER is hit on keyboard)
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        kwargs.setdefault('keyboard', None)
        super(MTTextInput, self).__init__(**kwargs)
        self._keyboard = kwargs.get('keyboard')
        self.original_width = self.width
        self.is_active_input = False
        self.padding = 20

        self.register_event_type('on_text_change')
        self.register_event_type('on_text_validate')

    def _get_keyboard(self):
        if not self._keyboard:
            self._keyboard = MTVKeyboard()
        return self._keyboard
    def _set_keyboard(self, value):
        if self._keyboard is not None:
            self._keyboard.remove_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up
            )
        self._keyboard = value
    keyboard = property(_get_keyboard, _set_keyboard)

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
        '''Show the associed keyboard of this widget.'''
        if self.is_active_input:
            return
        w = self.get_parent_window()
        w.add_widget(self.keyboard)
        w.push_handlers(on_keyboard=self._window_on_keyboard)
        self.is_active_input = True
        if self._keyboard is not None:
            self._keyboard.push_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up
            )
            self._keyboard.text = self.label

    def hide_keyboard(self):
        '''Hide the associed keyboard of this widget.'''
        if not self.is_active_input:
            return
        w = self.get_parent_window()
        w.remove_widget(self.keyboard)
        w.remove_handlers(on_keyboard=self._window_on_keyboard)
        self.is_active_input = False
        if self._keyboard is not None:
            self._keyboard.remove_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up
            )

    def draw(self):
        if self.is_active_input:
            set_color(*self.style.get('bg-color'))
            kx, ky = self.keyboard.to_window(*self.keyboard.center)
            kx, ky = self.to_widget(kx, ky)
            drawLine([self.center[0], self.center[1], kx, ky])
        if self.state[0] == 'down':
            set_color(0.5,0.5,0.5,0.5)
            drawCSSRectangle((self.x,self.y) , (self.width, self.height), style=self.style)
        else:
            set_color(*self.style.get('bg-color'))
            drawCSSRectangle((self.x,self.y) , (self.width, self.height), style=self.style)
        self.label_obj.draw()

    def _window_on_keyboard(self, key, scancode=None, unicode=None):
        if key == 27: # escape
            self.hide_keyboard()
            return True
        elif key == 8: # backspace
            key = (None, None, 'backspace', 1)
            self.keyboard.dispatch_event('on_key_down', key)
            self.keyboard.dispatch_event('on_key_up', key)
        elif key in (13, 271): # enter or numenter
            key = (None, None, 'enter', 1)
            self.keyboard.dispatch_event('on_key_down', key)
            self.keyboard.dispatch_event('on_key_up', key)
        else:
            if unicode is not None:
                self.keyboard.text = self.keyboard.text + unicode
            else:
                # oh god :[
                self.keyboard.text = self.keyboard.text + chr(key)


# Register all base widgets
MTWidgetFactory.register('MTTextInput', MTTextInput)
