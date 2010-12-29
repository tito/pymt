'''
TextInput: a text input who instance vkeyboard if needed
'''

__all__ = ('MTTextInput', )

from pymt.logger import pymt_logger
from pymt.base import getWindow
from pymt.config import pymt_config
from pymt.graphx import set_color, drawCSSRectangle, drawLine
from pymt.core.clipboard import Clipboard
from pymt.ui.widgets.button import MTButton
from pymt.ui.animation import Animation, AnimationAlpha
from pymt.ui.widgets.composed.vkeyboard import MTVKeyboard

class MTTextInput(MTButton):
    '''
    A text input widget is a simple label widget that will pop up
    a virtual keyboard when touched any input of the virtual keyboard
    will then have effect on the TextInput widget.

    .. versionadded:: 0.5.1
        Support of scrolling textarea, controlled by `scroll` attribute. You can
        now scroll inside the text area without editing text.

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
        `scroll`: bool, default to True
            If True, the scrolling of a text area is allowed.
        `scroll_trigger`: int, default to 10
            If scrolling is detected, don't fire event to show/hide keyboard.
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
        kwargs.setdefault('group', None)
        kwargs.setdefault('switch', True)
        kwargs.setdefault('keyboard_type',
            pymt_config.get('widgets', 'keyboard_type'))

        super(MTTextInput, self).__init__(**kwargs)

        self.register_event_type('on_text_change')
        self.register_event_type('on_text_validate')

        self._scroll_x = 0
        self._can_deactive = True
        self._keyboard = kwargs.get('keyboard')
        self._is_active_input = False

        #: Boolean to activate the password mode on the textinput.
        #: If true, it will show star instead of real characters
        self.password = kwargs.get('password', False)

        #: Boolean to control the scrolling of the textinput content
        self.scroll = kwargs.get('scroll', True)

        #: If the scroll if more than scroll_trigger, no event will be
        #: dispatched, and no show/hide of keyboard.
        self.scroll_trigger = kwargs.get('scroll_trigger', 10)

        #: Keyboard type (virtual or real)
        self.keyboard_type = kwargs.get('keyboard_type')

        #: If True, the keyboard is added to root window, not to parent window.
        self.keyboard_to_root = kwargs.get('keyboard_to_root')

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

        self.interesting_keys = {8: 'backspace', 13: 'enter', 127: 'del',
                                 271: 'enter', 273: 'cursor_up', 274: 'cursor_down',
                                 275: 'cursor_right', 276: 'cursor_left',
                                 278: 'cursor_home', 279: 'cursor_end',
                                 280: 'cursor_pgup', 281: 'cursor_pgdown',
                                 303: 'shift_L', 304: 'shift_R'}

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
                on_key_up=self._kbd_on_key_up,
                on_key_down=self._kbd_on_key_down
            )
        self._keyboard = value
    keyboard = property(_get_keyboard, _set_keyboard)

    def on_release(self, touch):
        if not self._can_deactive:
            return
        if self._is_active_input:
            self.hide_keyboard()
        else:
            self.show_keyboard()

    def _kbd_on_text_change(self, value):
        # reset scrolling when text is typed
        self._scroll_x = 0
        self.label = value
        self.dispatch_event('on_text_change', value)

    def _kbd_on_key_down(self, key, repeat=False):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            return
        elif internal_action == 'enter':
            self.hide_keyboard()
            self.dispatch_event('on_text_validate')
        elif internal_action == 'escape':
            self.hide_keyboard()

    def _kbd_on_key_up(self, key, repeat=False):
        pass

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
        if self._is_active_input:
            return
        self.deactivate_group()
        self._is_active_input = True

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
            self._keyboard.reset_repeat()
            self._keyboard.push_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up,
                on_key_down=self._kbd_on_key_down
            )
            self._keyboard.text = self.label

    def hide_keyboard(self):
        '''Hide the associed keyboard of this widget.'''
        if not self._is_active_input:
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
        self._is_active_input = False
        if self._keyboard is not None:
            self._keyboard.reset_repeat()
            self._keyboard.remove_handlers(
                on_text_change=self._kbd_on_text_change,
                on_key_up=self._kbd_on_key_up,
                on_key_down=self._kbd_on_key_down
            )

    def _window_on_key_down(self, key, scancode=None, unicode=None):
        modifiers = getWindow().modifiers
        if key == ord('v') and 'ctrl' in modifiers:
            text = Clipboard.get('text/plain')
            if text:
                self.keyboard.text += text
            return True

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
    value = property(_get_value, _set_value,
        doc='Get/set the value of the label')

    def _get_keyboard_type(self):
        return self._keyboard_type
    def _set_keyboard_type(self, t):
        self.hide_keyboard()
        self._keyboard_type = t
        if self._is_active_input:
            self.show_keyboard()
    keyboard_type = property(_get_keyboard_type, _set_keyboard_type,
        doc='Get/set the keyboard type to use')

    @property
    def is_active_input(self):
        '''Return True if the input is active'''
        return self._is_active_input

    #
    # Overload the touch down/move/up for :
    #   1. handle the switch button
    #   2. be able to scroll inside the text input
    #

    def on_touch_down(self, touch):
        # check if it's the switch button that collide.
        if self._switch and self._switch.collide_point(*touch.pos):
            self.hide_keyboard()
            if self.keyboard_type == 'virtual':
                self.keyboard_type = 'real'
            else:
                self.keyboard_type = 'virtual'
            self._switch.label = self.keyboard_type
            self.show_keyboard()
            return True
        # reset scrolling when a touch is comming
        # FIXME: can be not accurate if many touch are comming.
        if self.collide_point(*touch.pos):
            self._scroll_x = 0
            self._can_deactive = True
        # and only now, dispatch as usual.
        return super(MTTextInput, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if not super(MTTextInput, self).on_touch_move(touch):
            return
        # we got a valid touch, 
        self._scroll_x += touch.dxpos - touch.x
        self._can_deactive = True
        if abs(touch.x - touch.oxpos) > self.scroll_trigger and self.scroll:
            self._can_deactive = False
        return True

    def on_touch_up(self, touch):
        if super(MTTextInput, self).on_touch_up(touch):
            if not self.is_active_input:
                self._scroll_x = 0
                self._can_deactive = True
            return True

    def draw(self):
        if self._is_active_input and self.keyboard_type == 'virtual':
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
        set_color(*self.style.get('bg-color'))
        state = 'active' is self._is_active_input or None
        drawCSSRectangle(pos=self.pos, size=self.size,
                         style=self.style, state=state)

    def draw_label(self, dx=0, dy=0):
        # before drawing label, adjust the viewport position of the label. it's
        # a new feature that permit to draw only a part of the label.
        width = self._used_label.width - self.width
        scroll_x = self._scroll_x if self.scroll else 0
        if self.is_active_input:
            scroll_x = width + scroll_x
        if scroll_x > width:
            scroll_x = width
        if scroll_x < 0:
            scroll_x = 0
        self.viewport_pos = (scroll_x, 0)
        super(MTTextInput, self).draw_label(dx, dy)

    def on_update(self):
        super(MTTextInput, self).on_update()
        if self._switch:
            self._switch.pos = self.x + self.width - 60, self.y + self.height

