__all__ = ['MTFormInput']

from abstract import MTAbstractFormWidget
from ....graphx import set_color, drawRectangle
from ...factory import MTWidgetFactory
from ..vkeyboard import MTTextInput

class MTFormInput(MTTextInput):
    '''Form input : a one-line text input, with virtual-keyboard support
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', 16)
        super(MTFormInput, self).__init__(**kwargs)
        # get height of font-size
        self.label_obj.text = ' '
        self.height = self.label_obj.content_height
        self.label_obj.text = ''

    def draw(self):
        if self.state[0] == 'down':
            set_color(0.5,0.5,0.5,0.5)
        else:
            set_color(*self.color)
        drawRectangle(pos=self.pos, size=self.size)
        self.label_obj.x, self.label_obj.y = self.pos
        self.label_obj.draw()

    def on_resize(self, w, h):
        layout = self.get_parent_layout()
        if layout:
            layout.do_layout()
        super(MTFormInput, self).on_resize(w, h)


# Register all base widgets
MTWidgetFactory.register('MTFormInput', MTFormInput)
