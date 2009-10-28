'''
Form checkbox: a simple checkbox
'''

__all__ = ['MTFormCheckbox']

from ....graphx import set_color, drawRectangle
from ...factory import MTWidgetFactory
from abstract import MTAbstractFormWidget
from OpenGL.GL import GL_LINE_LOOP

class MTFormCheckbox(MTAbstractFormWidget):
    '''A simple checkbox

    :Parameters:
        `halign` : str, default is 'center'
            Horizontal alignement, can be 'left', 'center', 'right'
        `valign` : str, default is 'center'
            Vertical alignement, can be 'top', 'center', 'bottom'

    :Events:
        `on_check`
            Fired when checkbox change state
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'center')
        kwargs.setdefault('size', (20,20))
        super(MTFormCheckbox, self).__init__(**kwargs)
        self.halign     = kwargs.get('halign')
        self.valign     = kwargs.get('valign')
        self.checked    = False
        self.touchID    = 0

        self.register_event_type('on_check')

    def get_content_pos(self, content_width, content_height):
        x, y = self.pos
        if self.halign == 'left':
            pass
        elif self.halign == 'center':
            x = x + (self.width - content_width) / 2
        elif self.halign == 'right':
            x = x + self.width - content_width
        if self.valign == 'top':
            y = y + self.height - content_height
        elif self.valign == 'center':
            y = y + (self.height - content_height) / 2
        elif self.valign == 'bottom':
            pass
        return (x, y)

    def on_check(self, checked):
        pass

    def draw(self):
        pos = self.get_content_pos(20, 20)
        if self.checked:
            set_color(.5, .5, .5, 1)
            drawRectangle(pos=pos, size=(20,20))
        set_color(.7, .7, .7, 1)
        drawRectangle(pos=pos, size=(20,20), style=GL_LINE_LOOP)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchID = touch.id
            return True

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            return True

    def on_touch_up(self, touch):
        if self.touchID == touch.id and self.collide_point(touch.x, touch.y):
            self.checked = not self.checked
            self.dispatch_event('on_check', self.checked)
            return True

# Register all base widgets
MTWidgetFactory.register('MTFormCheckbox', MTFormCheckbox)
