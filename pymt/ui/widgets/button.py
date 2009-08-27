'''
Button package: implement different type of button
'''

from __future__ import with_statement
__all__ = ['MTButton', 'MTToggleButton', 'MTImageButton']

from pyglet.gl import *
from pyglet.text import Label
from ...image import Image
from ...graphx import GlDisplayList, set_color, gx_blending
from ...graphx import drawCSSRectangle
from ...utils import get_color_for_pyglet
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTButton(MTWidget):
    '''MTButton is a button implementation using MTWidget

    :Parameters:
        `label` : string, default is ''
            Label of button
        `anchor_x` : string
            X anchor of label, refer to pyglet.label.anchor_x documentation
        `anchor_y` : string
            Y anchor of label, refer to pyglet.label.anchor_x documentation
        `multiline` : bool, default is False
            Indicate if button is a multiline button

    :Styles:
        `color-down` : color
            Background-color of the button when it is press
        `bg-color` : color
            Background color of the slider
        `font-name` : str
            Name of font to use
        `font-size` : int
            Size of font in pixel
        `font-style` : str
            Style of font, can be "bold", "italic" or "bolditalic"
        `draw-border` : bool
            Indicate if the border must be drawed or not
        `border-radius` : int
            Size of radius in pixel
        `border-radius-precision` : float
            Precision of the radius drawing (1 mean no precision)
        `draw-text-shadow` : bool
            Indicate if the text shadow must be drawed
        `text-shadow-color` : color
            Color of the text shadow
        `text-shadow-position` : x y
            Relative position of shadow text
        `draw-alpha-background` : bool
            Indicate if the alpha background must be drawed

    :Events:
        `on_press`
            Fired when the button are pressed (not released)
        `on_release`
            Fired when the button are released
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('anchor_x', 'center')
        kwargs.setdefault('anchor_y', 'center')
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('width', 0)

        self.register_event_type('on_press')
        self.register_event_type('on_release')

        self.button_dl      = GlDisplayList()
        self._state         = ('normal', 0)
        self._label         = str(kwargs.get('label'))
        self.label_obj      = None

        super(MTButton, self).__init__(**kwargs)

        fw = self.style.get('font-weight')
        self.label_obj      = Label(
            font_name = self.style.get('font-name'),
            font_size = int(self.style.get('font-size')),
            bold = (fw in ('bold', 'bolditalic')),
            italic = (fw in ('italic', 'bolditalic')),
            anchor_x = kwargs.get('anchor_x'),
            anchor_y = kwargs.get('anchor_y'),
            text = kwargs.get('label'),
            multiline = kwargs.get('multiline'),
            width = kwargs.get('width')
        )

    def apply_css(self, styles):
        super(MTButton, self).apply_css(styles)
        if self.label_obj is not None:
            self.update_label()

    def update_label(self):
        fw = self.style.get('font-weight')
        self.label_obj.font_name = self.style.get('font-name')
        self.label_obj.font_size = self.style.get('font-size')
        self.label_obj.bold = (fw in ('bold', 'bolditalic'))
        self.label_obj.italic = (fw in ('italic', 'bolditalic'))
        self.button_dl.clear()

    def get_label(self):
        return self._label
    def set_label(self, text):
        self._label = str(text)
        self.label_obj.text = self._label
        self.button_dl.clear()
    label = property(get_label, set_label)

    def get_state(self):
        return self._state[0]
    def set_state(self, state):
        self._state = (state, 0)
    state = property(get_state, set_state, doc='Sets the state of the button, "normal" or "down"')

    def on_press(self, touch):
        pass

    def on_release(self, touch):
        pass

    def on_move(self, x, y):
        self.button_dl.clear()

    def on_resize(self, w, h):
        self.button_dl.clear()

    def draw(self):
        if self.get_state() == 'down':
            set_color(*self.style['color-down'])
        else:
            set_color(*self.style['bg-color'])

        if not self.button_dl.is_compiled():
            with self.button_dl:
                drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
                self.draw_label()
        self.button_dl.draw()

    def draw_label(self):
        if len(self._label) <= 0:
            return
        if self.style['draw-text-shadow']:
            with gx_blending:
                tsp = self.style['text-shadow-position']
                self.label_obj.x, self.label_obj.y = \
                    map(lambda x: self.pos[x] + self.size[x] / 2 + tsp[x], xrange(2))
                self.label_obj.color = get_color_for_pyglet(self.style['text-shadow-color'])
                self.label_obj.draw()
        self.label_obj.x, self.label_obj.y = \
            map(lambda x: self.pos[x] + self.size[x] / 2, xrange(2))
        self.label_obj.color = get_color_for_pyglet(self.style['font-color'])
        self.label_obj.draw()

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


class MTToggleButton(MTButton):
    '''Toggle button implementation, based on MTButton'''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', 'ToggleButton')
        super(MTToggleButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.get_state() == 'down':
                self._state = ('normal', touch.id)
            else:
                self._state = ('down', touch.id)
            self.dispatch_event('on_press', touch)
            return True

    def on_touch_move(self, touch):
        if self._state[1] == touch.id and not self.collide_point(touch.x, touch.y):
            return True

    def on_touch_up(self, touch):
        if self._state[1] == touch.id and self.collide_point(touch.x, touch.y):
            self.dispatch_event('on_release', touch)
            return True


class MTImageButton(MTButton):
    '''MTImageButton is a enhanced MTButton
    that draw an image instead of a text.

    :Parameters:
        `filename` : str
            Filename of image
        `scale` : float, default is 1.0
            Scaling of image, default is 100%, ie 1.0
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTImageButton')

        super(MTImageButton, self).__init__(**kwargs)
        self.image          = None
        self.scale          = kwargs.get('scale')
        self.filename		= kwargs.get('filename')
        self.size           = self.image.size

    def _get_filename(self):
        return self._filename
    def _set_filename(self, filename):
        self._filename = filename
        self.image     = Image(self.filename)
    filename = property(_get_filename, _set_filename)

    def draw(self):
        self.image.pos  = self.pos
        self.image.scale= self.scale
        self.size       = self.image.size
        self.image.draw()


MTWidgetFactory.register('MTToggleButton', MTToggleButton)
MTWidgetFactory.register('MTButton', MTButton)
MTWidgetFactory.register('MTImageButton', MTImageButton)
