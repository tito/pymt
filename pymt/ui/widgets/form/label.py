from abstract import MTAbstractFormWidget
from pyglet import *
from pymt.graphx import *
from pymt.ui.factory import MTWidgetFactory

class MTFormLabel(MTAbstractFormWidget):
    '''Form label : a simple text label with aligmenent support

    :Parameters:
        `label` : str, default is ''
            Text of label
        `font_name` : str, default is None
            Font name
        `font_size` : int, default is 16
            Font size
        `font_style` : str, default is None
            Style of font, can be 'bold', 'italic', 'bolditalic'
        `font_color` : list, default is (1,1,1,1)
            Font color
        `multiline` : bool, default is False
            Indicate if label is multiline. You should indicate a width :)
        `halign` : str, default is 'center'
            Horizontal alignement, can be 'left', 'center', 'right'
        `valign` : str, default is 'center'
            Vertical alignement, can be 'top', 'center', 'bottom'
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'center')
        kwargs.setdefault('font_name', None)
        kwargs.setdefault('font_size', 12)
        kwargs.setdefault('font_style', None)
        kwargs.setdefault('font_color', (1,1,1,1))
        kwargs.setdefault('multiline', False)
        super(MTFormLabel, self).__init__(**kwargs)
        self.font_name  = kwargs.get('font_name')
        self.font_size  = kwargs.get('font_size')
        self.font_style = kwargs.get('font_style')
        self.font_color = kwargs.get('font_color')
        self.multiline  = kwargs.get('multiline')
        self.label      = kwargs.get('label')
        self.halign     = kwargs.get('halign')
        self.valign     = kwargs.get('valign')

    def _get_label(self):
        return self._label
    def _set_label(self, label):
        self._label = label
        opts = {}
        opts['anchor_y'] = 'bottom'
        if self.font_name:
            opts['font_name'] = self.font_name
        if self.font_size:
            opts['font_size'] = self.font_size
        if self.font_style:
            if self.font_style in ['italic', 'bolditalic']:
                opts['italic'] = True
            if self.font_style in ['bold', 'bolditalic']:
                opts['bold'] = True
        opts['color'] = map(lambda x: x * 255, self.font_color)
        opts['text'] = label
        if self.multiline:
            opts['multiline'] = self.multiline
            opts['width'] = self.width
            print opts

        self._label_obj = Label(**opts)
        self.size = self._label_obj.content_width, self._label_obj.content_height
    label = property(_get_label, _set_label)

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

    def draw(self):
        self._label_obj.x, self._label_obj.y = self.get_content_pos(
            self._label_obj.content_width, self._label_obj.content_height)
        self._label_obj.draw()


# Register all base widgets
MTWidgetFactory.register('MTFormLabel', MTFormLabel)
