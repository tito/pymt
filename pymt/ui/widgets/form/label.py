'''
Form label: A text-label with align support
'''

__all__ = ['MTFormLabel']

from pymt.core.text import Label
from abstract import MTAbstractFormWidget
from ...factory import MTWidgetFactory

class MTFormLabel(MTAbstractFormWidget):
    '''Form label : a simple text label with alignment support

    :Parameters:
        `label` : str, default is ''
            Text of label
        `multiline` : bool, default is False
            Indicate if label is multiline. You should indicate a width :)
        `halign` : str, default is 'center'
            Horizontal alignement, can be 'left', 'center', 'right'
        `valign` : str, default is 'center'
            Vertical alignement, can be 'top', 'center', 'bottom'

    :Styles:
        `font-name` : str
            Font name
        `font-size` : int
            Font size
        `font-weight` : str
            Style of font, can be 'bold', 'italic', 'bolditalic'
        `font-color` : list
            Font color
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'center')
        kwargs.setdefault('multiline', False)
        super(MTFormLabel, self).__init__(**kwargs)
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
        if self.style.get('font-name') != '':
            opts['font_name'] = self.style.get('font-name')
        if int(self.style.get('font-size')) > 0:
            opts['font_size'] = int(self.style.get('font-size'))
        if self.style.get('font-weight'):
            if self.style.get('font-weight') in ['italic', 'bolditalic']:
                opts['italic'] = True
            if self.style.get('font-weight') in ['bold', 'bolditalic']:
                opts['bold'] = True
        opts['color'] = map(lambda x: int(x * 255), self.style.get('font-color'))
        opts['text'] = label
        if self.multiline:
            opts['multiline'] = self.multiline
            opts['width'] = self.width
            print opts

        self._label_obj = Label(label=label, **opts)
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
