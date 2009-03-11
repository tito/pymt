from __future__ import with_statement
__all__ = ['MTButton', 'MTToggleButton', 'MTImageButton']

from pyglet.gl import *
from pyglet.text import Label
from ...graphx import drawRectangle, drawRoundedRectangle, gx_matrix, GlDisplayList, set_color, gx_blending, DO
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTButton(MTWidget):
    '''MTButton is a button implementation using MTWidget

    :Parameters:
        `label` : string, default is ''
            Label of button
        `color_down` : list, default is (.5, .5, .5, .5)
            Color of button when pushed
        `anchor_x`: string
            X anchor of label, refer to pyglet.label.anchor_x documentation
        `anchor_y`: string
            Y anchor of label, refer to pyglet.label.anchor_x documentation
        `font_size`: integer, default is 10
            Font size of label
        `bold`: bool, default is True
            Font bold of label
        `border_radius`: float, default is 0
            Radius of background border
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('anchor_x', 'center')
        kwargs.setdefault('anchor_y', 'center')
        kwargs.setdefault('font_size', 10)
        kwargs.setdefault('bold', True)
        kwargs.setdefault('border_radius', 0)

        super(MTButton, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')

        self._button_dl     = GlDisplayList()
        self._state         = ('normal', 0)
        self.clickActions   = []
        self._label         = str(kwargs.get('label'))
        self.label_obj      = Label(
            font_size=kwargs.get('font_size'),
            bold=kwargs.get('bold'),
            anchor_x=kwargs.get('anchor_x'),
            anchor_y=kwargs.get('anchor_y'),
            text=kwargs.get('label')
        )
        if kwargs.has_key('color_down'):
            self.color_down = kwargs.get('color_down')
        self.border_radius  = kwargs.get('border_radius')

    def apply_css(self, styles):
        if styles.has_key('color-down'):
            self.color_down = styles.get('color-down')
        super(MTButton, self).apply_css(styles)

    def get_label(self):
        return self._label
    def set_label(self, text):
        self._label = str(text)
        self.label_obj.text = self._label
        self._button_dl.clear()
    label = property(get_label, set_label)

    def get_state(self):
        return self._state[0]
    def set_state(self, state):
        self._state = (state, 0)
    state = property(get_state, set_state, doc='Sets the state of the button, "normal" or "down"')

    def on_press(self, touchID, x, y):
        pass

    def on_release(self, touchID, x, y):
        pass

    def on_resize(self, w, h):
        self._button_dl.clear()

    def draw(self):
        # Select color
        if self._state[0] == 'down':
            set_color(*self.color_down)
        else:
            set_color(*self.bgcolor)

        with DO(gx_matrix, gx_blending):
            glTranslatef(self.x, self.y, 0)

            # Construct display list if possible
            if not self._button_dl.is_compiled():
                with self._button_dl:
                    if self.border_radius > 0:
                        drawRoundedRectangle(size=self.size, radius=self.border_radius)
                    else:
                        drawRectangle(size=self.size)
                    if len(self._label):
                        self.label_obj.x, self.label_obj.y = self.width/2 , self.height/2
                        self.label_obj.draw()
            self._button_dl.draw()

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self._state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x,y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self._state[1] == touchID and not self.collide_point(x,y):
            self._state = ('normal', 0)
            return True
        return self.collide_point(x,y)

    def on_touch_up(self, touches, touchID, x, y):
        if self._state[1] == touchID and self.collide_point(x,y):
            self._state = ('normal', 0)
            self.dispatch_event('on_release', touchID, x,y)
            return True
        return self.collide_point(x,y)


class MTToggleButton(MTButton):
    '''Toggle button implementation, based on MTButton'''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', 'ToggleButton')
        super(MTToggleButton, self).__init__(**kwargs)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            if self.get_state() == 'down':
                self._state = ('normal', touchID)
            else:
                self._state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x,y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self._state[1] == touchID and not self.collide_point(x,y):
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self._state[1] == touchID and self.collide_point(x,y):
            self.dispatch_event('on_release', touchID, x,y)
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
        # Preserve this way to do
        # Later, we'll give another possibility, like using a loader...
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTImageButton')

        super(MTImageButton, self).__init__(**kwargs)
        img                 = pyglet.image.load(kwargs.get('filename'))
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
        self.image.scale    = self.scale
        self.size           = (self.image.width, self.image.height)

    def draw(self):
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = self.scale
        self.size           = (self.image.width, self.image.height)
        self.image.draw()

MTWidgetFactory.register('MTToggleButton', MTToggleButton)
MTWidgetFactory.register('MTButton', MTButton)
MTWidgetFactory.register('MTImageButton', MTImageButton)
