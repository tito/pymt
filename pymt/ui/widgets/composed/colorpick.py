'''
Color picker: a simple color picker with 3 slider
'''

__all__ = ('MTColorPicker', )

from pymt.graphx import set_color, drawRectangle, GlDisplayList, \
        drawCSSRectangle
from pymt.ui.widgets.layout import MTBoxLayout
from pymt.ui.widgets.scatter import MTScatterWidget
from pymt.ui.widgets.slider import MTSlider

class MTColorPicker(MTScatterWidget):
    '''MTColorPicker is a implementation of a color picker using MTWidget

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 255
            Maximum value of slider
        `targets` : list, default is []
            List of widget to be affected by change
        `values` : list, default is [77, 77, 77]
            Default value of slider for RGB (0-255)
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 255)
        kwargs.setdefault('values', [77, 77, 77])
        kwargs.setdefault('targets', [])
        self.dl = GlDisplayList()
        super(MTColorPicker, self).__init__(**kwargs)
        self.size = (130, 290)
        self.targets = kwargs.get('targets')
        self.sliders = [
            MTSlider(min=kwargs.get('min'), max=kwargs.get('max'),
                     size=(30, 200),  style={'slider-color': (1, 0, 0, 1)},
                     cls='colorpicker-slider'),
            MTSlider(min=kwargs.get('min'),  max=kwargs.get('max'),
                     size=(30, 200),  style={'slider-color': (0, 1, 0, 1)},
                     cls='colorpicker-slider'),
            MTSlider(min=kwargs.get('min'),  max=kwargs.get('max'),
                     size=(30, 200),  style={'slider-color': (0, 0, 1, 1)},
                     cls='colorpicker-slider')
        ]
        vbox = MTBoxLayout(spacing=10, padding=10)
        for slider in self.sliders:
            slider.value = 77
            slider.push_handlers(on_value_change=self.update_color)
            vbox.add_widget(slider)
        self.add_widget(vbox)
        self.update_color()
        self.touch_positions = {}

    def apply_css(self, styles):
        super(MTColorPicker, self).apply_css(styles)
        self.dl.clear()

    def draw(self):
        if not self.dl.is_compiled():
            with self.dl:
                set_color(*self.style['bg-color'])
                drawCSSRectangle(size=self.size, style=self.style)

                set_color(*self.current_color)
                drawRectangle(pos=(10, 220), size=(110, 60))
        self.dl.draw()

    def update_color(self, *largs):
        r = self.sliders[0].value / 255.
        g = self.sliders[1].value / 255.
        b = self.sliders[2].value / 255.
        for w in self.targets:
            w.color = (r, g, b, 1)
        self.current_color = (r, g, b, 1.0)
        self.dl.clear()
