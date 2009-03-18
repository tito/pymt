'''
Form slider: a slider based on MTSlider + MTLabel
'''

__all__ = ['MTFormSlider']

from ....graphx import set_color, drawRectangle
from ...factory import MTWidgetFactory
from ..slider import MTSlider
from ..layout import MTBoxLayout
from abstract import MTAbstractFormWidget
from label import MTFormLabel

class MTFormSlider(MTAbstractFormWidget):
    '''MTSlider is an implementation of a scrollbar using MTWidget.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `value` : int, default is `min`
            Default value of slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 10)
        kwargs.setdefault('value', None)
        super(MTFormSlider, self).__init__(**kwargs)
        self._value = kwargs.get('min')
        if kwargs.get('value'):
            self._value = kwargs.get('value')
        self.layout = MTBoxLayout(orientation='horizontal', spacing=8)
        self.slider = MTSlider(orientation='horizontal', min=kwargs.get('min'),
                              max=kwargs.get('max'), value=kwargs.get('value'),
                              size=(200,30))
        self.layout.add_widget(self.slider)
        self.label = MTFormLabel(label=str(int(self.value)), font_style='bold', font_size=16)
        self.layout.add_widget(self.label)
        # FIXME: don't add 20, try to figure the good value
        # Ideal: (Label(text=str(self.max)).content_width)
        self.size = (self.layout.content_width + 40, self.layout.content_height)
        self._add_widget(self.layout)
        self.slider.push_handlers(on_value_change=self.on_value_change)

    def on_value_change(self, value):
        self._value = value
        self.label.label = str(int(value))

    def _set_value(self, value):
        self._value = value
        self.label.label = str(int(value))
        self.slider.value = int(value)
    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def _set_max(self, max):
        self.slider.max = max
    def _get_max(self):
        return self.slider.max
    max = property(_get_max, _set_max)

    def _set_min(self, min):
        self.slider.min = min
    def _get_min(self):
        return self.slider.min
    min = property(_get_min, _set_min)

    def draw(self):
        super(MTFormSlider, self).draw()

    def on_move(self, x, y):
        super(MTFormSlider, self).on_move(x, y)
        self.layout.pos = self.pos



# Register all base widgets
MTWidgetFactory.register('MTFormSlider', MTFormSlider)

