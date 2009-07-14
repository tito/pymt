'''
Form button: button for Form
'''

__all__ = ['MTFormButton']

from ....graphx import set_color, drawRoundedRectangle
from ...factory import MTWidgetFactory
from label import MTFormLabel

class MTFormButton(MTFormLabel):
    '''Form button : a simple button label with aligmenent support

    :Styles:
        `color-down` : list
            Background color of pushed button

    :Events:
        `on_press`
            Fired when button is pressed
        `on_release`
            Fired when button is released
    '''

    def __init__(self, **kwargs):
        super(MTFormButton, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        self._state         = ('normal', 0)

    def draw(self):
        if self._state[0] == 'down':
            set_color(*self.style.get('color-down'))
        else:
            set_color(*self.style.get('bg-color'))
        drawRoundedRectangle(pos=self.pos, size=self.size)
        super(MTFormButton, self).draw()

    def get_state(self):
        return self._state[0]
    def set_state(self, state):
        self._state = (state, 0)
    state = property(get_state, set_state, doc='Sets the state of the button, "normal" or "down"')

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self._state = ('down', touch.id)
            self.dispatch_event('on_press', touch)
            return True

    def on_touch_move(self, touch):
        if self._state[1] == touch.id and not self.collide_point(touch.x, touch.y):
            self._state = ('normal', 0)
            return True
        return self.collide_point(touch.x, touch.y)

    def on_touch_up(self, touch):
        if self._state[1] == touch.id and self.collide_point(touch.x, touch.y):
            self._state = ('normal', 0)
            self.dispatch_event('on_release', touch)
            return True
        return self.collide_point(touch.x, touch.y)


# Register all base widgets
MTWidgetFactory.register('MTFormButton', MTFormButton)
