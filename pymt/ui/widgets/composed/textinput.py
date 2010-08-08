'''
TextInput: a text input who instance vkeyboard if needed
'''

__all__ = ('MTTextInput', )

from pymt.config import pymt_config
from pymt.graphx import set_color, drawCSSRectangle, drawLine
from pymt.ui.widgets.button import MTButton
from pymt.ui.animation import Animation, AnimationAlpha
from pymt.ui.widgets.composed.vkeyboard import MTVKeyboard

class MTTextInput(MTButton):
    '''
    A text input widget is a simple label widget that will pop up
    a virtual keyboard when touched any input of the virtual keyboard
    will then have effect on the TextInput widget.

    :Parameters:
        `keyboard`: MTVkeyboard object, default to None
            Use another MTVKeyboard than the default one
        `keyboard_to_root`: bool, defaults to False.
            Indicate whether the keyboard should be attached to the root
            window. If True, this will have the effect of the keyboard being
            raised above other widgets.
        `keyboard_type`: str, default to config.
            Configuration section is 'widgets', token 'keyboard_type'.
            Can be one of 'virtual' or 'real'. If real, the virtual keyboard
            will be not showed
        `password`: bool, default to False
            If True, the label will be showed with star
        `group`: str, default to random
            If the group is the same for multiple text input
            You can switch between them with TAB, and use the same keyboard.
        `switch`: bool, default to True
            If True, a switch button will be show to switch from real or virtual
            keyboard
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
        kwargs.setdefault('halign', 'left')
        kwargs.setdefault('keyboard', None)
        kwargs.setdefault('keyboard_to_root', False)
        kwargs.setdefault('password', False)
        kwargs.setdefault('group', None)
        kwargs.setdefault('switch', True)
        kwargs.setdefault('keyboard_type',
            pymt_config.get('widgets', 'keyboard_type'))
        super(MTTextInput, self).__init__(**kwargs)
        self._keyboard = kwargs.get('keyboard')
        self.is_active_input = False
        self.password = kwargs.get('password')

        # initialize group on random if nothing is set
        self._groupname = kwargs.get('group')
        if self._groupname is None:
            MTTextInput._group_id += 1
            self._groupname = 'uniqgroup%d' % MTTextInput._group_id
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

        # switch button between vkeyboard or hardware
        self._switch = None
        if kwargs.get('switch'):
            self._switch = MTButton(
                label=kwargs.get('keyboard_type'), cls='switch-button',
                size=(60, 20), font_size=8,
                pos=(self.x + self.width - 60, self.y + self.height))

        self.keyboard_type = kwargs.get('keyboard_type')
        self.keyboard_to_root = kwargs.get('keyboard_to_root')

        self.interesting_keys = {8: 'backspace', 13: 'enter', 127: 'del',
                                 271: 'enter', 273: 'cursor_up', 274: 'cursor_down',
                                 275: 'cursor_right', 276: 'cursor_left',
                                 278: 'cursor_home', 279: 'cursor_end',
                                 280: 'cursor_pgup', 281: 'cursor_pgdown'}

    def on_resize(self, *largs):
        if hasattr(self, '_switch'):
            self._switch.pos = self.x + self.width - 60, self.y + self.height
        return super(MTTextInput, self).on_resize(*largs)

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

    def _kbd_on_key_up(self, key, repeat=False):
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
        self.is_active_input = True

        # activate switch button if necessary
        if self._switch:
            self.add_widget(self._switch)

        # activate the real keyboard
        w = self.get_root_window()
        w.push_handlers(on_key_down=self._window_on_key_down,
                        on_key_up=self._window_on_key_up)

        # activate the virtual keyboard
        if self.keyboard_type == 'virtual':
            to_root = self.keyboard_to_root
            w = self.get_root_window() if to_root else self.get_parent_window()
            w.add_widget(self.keyboard)
        if self.keyboard is not None:
            self._keyboard.push_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up
            )
            self._keyboard.text = self.label

    def hide_keyboard(self):
        '''Hide the associed keyboard of this widget.'''
        if not self.is_active_input:
            return
        if self._switch:
            self.remove_widget(self._switch)
        parent = self.keyboard.parent
        if parent is not None:
            # If keyboard type is real, the keyboard is not attached to any
            # parent widget.
            parent.remove_widget(self.keyboard)
        w = self.get_root_window()
        w.remove_handlers(on_key_down=self._window_on_key_down,
                          on_key_up=self._window_on_key_up)
        self.is_active_input = False
        if self._keyboard is not None:
            self._keyboard.remove_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up
            )

    def on_update(self):
        super(MTTextInput, self).on_update()
        if self._switch:
            self._switch.pos = self.x + self.width - 60, self.y + self.height

    def draw(self):
        if self.is_active_input and self.keyboard_type == 'virtual':
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

    def _window_on_key_down(self, key, scancode=None, unicode=None):
        if key == 27: # escape
            self.hide_keyboard()
            return True
        elif key == 9: # tab
            self.focus_next()
            return True
        if not self.keyboard:
            return
        k = self.interesting_keys.get(key)
        if k:
            key = (None, None, k, 1)
            self.keyboard.dispatch_event('on_key_down', key)
        else:
            if unicode is not None:
                self.keyboard.text += unicode
            else:
                self.keyboard.text += chr(key)

    def _window_on_key_up(self, key, scancode=None, unicode=None):
        k = self.interesting_keys.get(key)
        if k and self.keyboard:
            key = (None, None, k, 1)
            self.keyboard.dispatch_event('on_key_up', key)

    def _get_value(self):
        return self.label
    def _set_value(self, value):
        self.label = value
    value = property(
        lambda self: self._get_value(),
        lambda self, x: self._set_value(x),
        doc='Get/set the value of the label')

    def _get_keyboard_type(self):
        return self._keyboard_type
    def _set_keyboard_type(self, t):
        self.hide_keyboard()
        self._keyboard_type = t
        if self.is_active_input:
            self.show_keyboard()
    keyboard_type = property(
        lambda self: self._get_keyboard_type(),
        lambda self, x: self._set_keyboard_type(x),
        doc='Get/set the keyboard type to use')

    #
    # Needed if the switch button must be replaced
    #

    def on_touch_down(self, touch):
        if self._switch and self._switch.collide_point(*touch.pos):
            self.hide_keyboard()
            if self.keyboard_type == 'virtual':
                self.keyboard_type = 'real'
            else:
                self.keyboard_type = 'virtual'
            self._switch.label = self.keyboard_type
            self.show_keyboard()
            return True
        return super(MTTextInput, self).on_touch_down(touch)

