'''
Button package: implement different type of button
'''


__all__ = ['MTButton', 'MTToggleButton', 'MTImageButton']

import pymt
from OpenGL.GL import *
from ...graphx import GlDisplayList, set_color, gx_blending
from ...graphx import drawCSSRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget
from label import MTLabel

class MTButton(MTLabel):
    '''MTButton is a button implementation using MTLabel

    :Parameters:
        `label` : string, default is ''
            Label of button
        `anchor_x` : string, default to 'center'
            Horizontal alignment of label inside button (left, center, right)
        `anchor_y` : string, default to 'center'
            Vertical alignment of label inside button (bottom, center, top)
        `multiline` : bool, default is False
            Indicate if button is a multiline button

    :Styles:
        `color-down` : color
            Background-color of the button when it is press
        `bg-color` : color
            Background color of the button
        `color` : color
            color of the text/label on teh button
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
        `on_press` (touch object, )
            Fired when the button are pressed (not released)
        `on_release` (touch object, )
            Fired when the button are released
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('autosize', False)
        kwargs.setdefault('autowidth', False)
        kwargs.setdefault('autoheight', False)
        kwargs.setdefault('anchor_x', 'center')
        kwargs.setdefault('anchor_y', 'center')
        # FIXME, would be nice to suppress it !
        kwargs.setdefault('size', (100, 100))
        self._state         = ('normal', 0)
        super(MTButton, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        if self._state[1] != 0:
            return False
        self._state = ('down', touch.id)
        self.dispatch_event('on_press', touch)
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        # take the grabbed touch for us.
        if not touch.grab_current == self:
            return False
        return True

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return False
        touch.ungrab(self)
        self._state = ('normal', 0)
        self.dispatch_event('on_release', touch)
        return True

    def get_state(self):
        return self._state[0]
    def set_state(self, state):
        self._state = (state, 0)
    state = property(get_state, set_state,
                     doc='Sets the state of the button, "normal" or "down"')

    def update_label(self):
        pass

    def draw_background(self):
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style,
                         state=self.state)

    def draw_label(self, dx=0, dy=0):
        if self.style['draw-text-shadow']:
            tsp = self.style['text-shadow-position']
            tsp[0] += dx
            tsp[1] += dy
            old_color = self.kwargs.get('color')
            self.kwargs['color'] = self.style['text-shadow-color']

            super(MTButton, self).draw_label(*tsp)
            self.kwargs['color'] = old_color
        super(MTButton, self).draw_label(dx, dy)


class MTToggleButton(MTButton):
    '''Toggle button implementation, based on MTButton'''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', 'ToggleButton')
        super(MTToggleButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        #if self._state[1] != 0:
        #    return False
        if self.get_state() == 'down':
            self._state = ('normal', 0)
        else:
            self._state = ('down', touch.id)
        self.dispatch_event('on_press', touch)
        touch.grab(self)
        return True

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return False
        touch.ungrab(self)
        self._state = (self.state, 0)
        self.dispatch_event('on_release', touch)
        return True


class MTImageButton(MTButton):
    '''MTImageButton is a enhanced MTButton
    that draw an image instead of a text.

    :Parameters:
        `filename` : str
            Filename of image
        `image` : Image
            Instead of giving a filename, give a Image object
        `scale` : float, default is 1.0
            Scaling of image, default is 100%, ie 1.0
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('filename', None)
        kwargs.setdefault('image', None)
        if kwargs.get('filename') is None and kwargs.get('image') is None:
            raise Exception('No filename or image given to MTImageButton')

        super(MTImageButton, self).__init__(**kwargs)
        self.image          = kwargs.get('image')
        self.scale          = kwargs.get('scale')
        self.filename       = kwargs.get('filename')
        self.size           = self.image.size

    def _get_filename(self):
        return self._filename
    def _set_filename(self, filename):
        self._filename = filename
        if filename:
            self.image = pymt.Image(self.filename)
    filename = property(_get_filename, _set_filename)

    def draw(self):
        self.image.pos      = self.pos
        self.image.scale    = self.scale
        s                   = self.image.size
        self.size           = s[0] * self.scale, s[1] * self.scale
        self.image.draw()


MTWidgetFactory.register('MTToggleButton', MTToggleButton)
MTWidgetFactory.register('MTButton', MTButton)
MTWidgetFactory.register('MTImageButton', MTImageButton)
