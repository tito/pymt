'''
TextInput: a text input who instance vkeyboard if needed
'''

__all__ = ['MTTextInput']

from ....graphx import set_color, drawCSSRectangle, drawLine, GlDisplayList
from ..button import MTButton
from ...factory import MTWidgetFactory
from ...animation import Animation, AnimationAlpha
from vkeyboard import MTVKeyboard

class MTTextInput(MTButton):
    '''
    A text input widget is a simple label widget that will pop up
    a virtual keyboard when touched any input of the virtual keyboard
    will then have effect on the TextInput widget.

    :Parameters:
        `keyboard`: MTVkeyboard object, default to None
            Use another MTVKeyboard than the default one
        `password`: bool, default to False
            If True, the label will be showed with star
        `group`: str, default to random
            If the group is the same for multiple text input
            You can switch between them with TAB, and use the same keyboard.

    :Events:
        `on_text_change` (text)
            Fired when the content of text input is changed
        `on_text_validate` ()
            Fired when the text is validate (when ENTER is hit on keyboard)
    '''
    _group_id = 0
    _group = {}

    def __init__(self, **kwargs):
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'center')
        kwargs.setdefault('keyboard', None)
        kwargs.setdefault('padding', 20)
        kwargs.setdefault('password', False)
        kwargs.setdefault('group', None)
        super(MTTextInput, self).__init__(**kwargs)
        self._keyboard = kwargs.get('keyboard')
        self.original_width = None
        self.is_active_input = False
        self.password = kwargs.get('password')

        # initialize group on random if nothing is set
        self._groupname = kwargs.get('group')
        if self._groupname is None:
            self._group_id += 1
            self._groupname = 'uniqgroup%d' % self._group_id
        # first time ? create the group
        if not self._groupname in self._group:
            self.group['keyboard'] = None
            self.group['widgets'] = []
        self.group['widgets'].append(self)

        self.register_event_type('on_text_change')
        self.register_event_type('on_text_validate')

        # save original color for error
        self._notify_bg_color = self.style['bg-color']
        self._notify_bg_color_active = self.style['bg-color-active']
        self._notify_animation = None

    def _get_keyboard(self):
        if not self._keyboard:
            self._keyboard = self.group['keyboard']
            if self._keyboard is None:
                self._keyboard = MTVKeyboard()
                self.group['keyboard'] = self._keyboard
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

    def _kbd_on_text_change(self, value):
        self.label = value
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

    @property
    def group(self):
        '''Return information (keyboard/widget list) from the current
        group of the widget'''
        if not self._groupname in self._group:
            self._group[self._groupname] = {}
        return self._group[self._groupname]

    def notify_error(self):
        '''Call this function to make animation on background as an error
        '''
        error_color = self.style['bg-color-error']
        if self._notify_animation is not None:
            self._notify_animation.stop()
        self.style['bg-color'] = self._notify_bg_color
        self.style['bg-color-active'] = self._notify_bg_color_active
        self._notify_animation = self.do(Animation(
            style={'bg-color': error_color, 'bg-color-active': error_color},
            f=lambda x: 1 - AnimationAlpha.ease_in_out_quart(x)))

    def deactivate_group(self):
        '''Deactivate all widgets in the group'''
        for w in self.group['widgets']:
            w.hide_keyboard()

    def focus_next(self):
        '''Focus the next textinput in the list'''
        idx = (self.group['widgets'].index(self) + 1)
        idx = idx % len(self.group['widgets'])
        widget = self.group['widgets'][idx]
        widget.show_keyboard()

    def show_keyboard(self):
        '''Show the associed keyboard of this widget.'''
        if self.is_active_input:
            return
        self.deactivate_group()
        w = self.get_parent_window()
        w.add_widget(self.keyboard)
        w = self.get_root_window()
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
        w = self.get_root_window()
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

        if self.password:
            pw = '*' * len(self.label)
            old_label = self.label
            self.label = pw
        super(MTTextInput, self).draw()
        if self.password:
            self.label = old_label

    def draw_background(self):
        if self.is_active_input:
            set_color(*self.style.get('bg-color'))
            drawCSSRectangle(pos=self.pos, size=self.size, style=self.style,
                            state='active')
        else:
            set_color(*self.style.get('bg-color'))
            drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

    def _window_on_keyboard(self, key, scancode=None, unicode=None):
        if key == 27: # escape
            self.hide_keyboard()
            return True
        elif key == 9: # tab
            self.focus_next()
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
