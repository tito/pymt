'''
Slider package: provide multiple slider implementation (simple, xy, boundary...)
'''

from __future__ import division

__all__ = ('MTSlider', 'MTXYSlider', 'MTBoundarySlider', 'MTMultiSlider')

import random
from pymt.ui.widgets.widget import MTWidget
from pymt.graphx import drawRectangle, drawCircle, drawLabel, set_color, \
        drawCSSRectangle

class MTSlider(MTWidget):
    '''MTSlider is an implementation of a scrollbar using MTWidget.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `orientation` : str, default is vertical
            Type of orientation, can be 'horizontal' or 'vertical'
        `value` : int, default is `min`
            Default value of slider
        `value_show` : bool, default to False
            Show value on the slider
        `value_format` : str, default to '%d'
            If value is showed, this is the format used for drawing value
        `value_config` : dict, default to {}
            Settings to pass to drawLabel()
    :Styles:
        `slider-color` : color
            Color of the slider
        `slider-color-down` : color
            Color of the slider when pressed down (same as slider-color by default)
        `bg-color` : color
            Background color of the slider
        `padding` : int
            Padding of content

    :Events:
        `on_value_change` (value)
            Fired when slider value is changed
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('value_show', False)
        kwargs.setdefault('value_format', '%d')
        kwargs.setdefault('value_config', {})
        if kwargs.get('orientation') == 'vertical':
            kwargs.setdefault('size', (30, 400))
        else:
            kwargs.setdefault('size', (400, 30))
        kwargs.setdefault('value', None)

        super(MTSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts    = [] # only react to touch input that originated on this widget
        self.orientation    = kwargs.get('orientation')
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')
        self.value_show     = kwargs.get('value_show')
        self.value_format   = kwargs.get('value_format')
        self.value_config   = kwargs.get('value_config')
        self._value         = self.min
        if kwargs.get('value'):
            self._value = kwargs.get('value')

    def on_value_change(self, value):
        pass

    def set_value(self, _value):
        self._value = _value
        self.dispatch_event('on_value_change', self._value)
    def get_value(self):
        return self._value
    value = property(get_value, set_value, doc='Value of the slider')

    def draw(self):
        px, py = self.style['padding']
        px2, py2 = px / 2., py / 2.
        diff = self.max - self.min
        if self.orientation == 'vertical':
            if diff == 0:
                length = 0
            else:
                length = int((self._value - self.min) * \
                             (self.height - py) / diff)
            pos = self.x + px2, self.y + py2
            size = self.width - px, length
        else:
            if diff == 0:
                length = 0
            else:
                length = int((self._value - self.min) * \
                             (self.width - px) / diff)
            pos = self.x + px2, self.y + py2
            size = length, self.height - py

        # draw outer rectangle
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

        # draw inner rectangle
        if self.touchstarts:
            set_color(*self.style.get('slider-color-down'))
        else:
            set_color(*self.style.get('slider-color'))
        drawCSSRectangle(pos=pos, size=size, style=self.style, prefix='slider')

        if self.value_show:
            self.draw_value()

    def draw_value(self):
        drawLabel(self.value_format % (self.value), pos=self.center,
                  **self.value_config)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchstarts.append(touch.id)
            self.on_touch_move(touch)
            return True
        return super(MTSlider, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            last_value = self._value
            if self.orientation == 'vertical':
                self._value = (touch.y - self.y) * (self.max - self.min) / float(self.height) + self.min
            else:
                self._value = (touch.x - self.x) * (self.max - self.min) / float(self.width) + self.min
            if self._value >= self.max:
                self._value = self.max
            if self._value <= self.min:
                self._value = self.min
            if not self._value == last_value:
                self.dispatch_event('on_value_change', self._value)
            return True
        return super(MTSlider, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
        return super(MTSlider, self).on_touch_up(touch)

class MTXYSlider(MTWidget):
    '''MTXYSlider is an implementation of a 2D slider using MTWidget.

    :Parameters:
        `min_x` : int, default is 20
            Minimum value of slider
        `max_x` : int, default is 100
            Maximum value of slider
        `min_y` : int, default is 20
            Minimum value of slider
        `max_y` : int, default is 100
            Maximum value of slider
        `radius` : int, default is 200
            Radius of the slider handle
        `value_x` : int, default is `min_x`
            Default X value of slider
        `value_y` : int, default is `min_y`
            Default Y value of slider
    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider

    :Events:
        `on_value_change` (value X, value Y)
            Fired when slider x/y value is changed
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min_x', 20)
        kwargs.setdefault('max_x', 100)
        kwargs.setdefault('min_y', 20)
        kwargs.setdefault('max_y', 100)
        kwargs.setdefault('radius', 20)
        kwargs.setdefault('size', (200, 200))
        kwargs.setdefault('value_x', kwargs.get('min_x'))
        kwargs.setdefault('value_y', kwargs.get('min_y'))

        super(MTXYSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.radius     = kwargs.get('radius')
        self.padding    = kwargs.get('radius')
        self.min_x      = kwargs.get('min_x')
        self.max_x      = kwargs.get('max_x')
        self.min_y      = kwargs.get('min_y')
        self.max_y      = kwargs.get('max_y')
        self.radius     = kwargs.get('radius')
        self._value_x   = kwargs.get('value_x')
        self._value_y   = kwargs.get('value_y')

    def on_value_change(self, value_x, value_y):
        pass

    def set_value_x(self, value):
        self._value_x = value
        self.dispatch_event('on_value_change', self._value_x, self._value_y)
    def get_value_x(self):
        return self._value_x
    value_x = property(get_value_x, set_value_x, doc='Value of the slider (x axis)')

    def set_value_y(self, value):
        self._value_y = value
        self.dispatch_event('on_value_change', self._value_x, self._value_y)
    def get_value_y(self):
        return self._value_y
    value_y = property(get_value_y, set_value_y, doc='Value of the slider (y axis)')

    def draw(self):
        # draw outer rectangle
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

        # draw inner circle
        set_color(*self.style.get('slider-color'))
        pos_x = int((self._value_x - self.min_x) * (self.width - self.padding*2) / (self.max_x - self.min_x))  + self.x + self.padding
        pos_y = int((self._value_y - self.min_y) * (self.height - self.padding*2) / (self.max_y - self.min_y)) + self.y + self.padding
        drawCircle(pos=(pos_x, pos_y), radius=self.radius)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchstarts.append(touch.id)
            return True
        return super(MTXYSlider, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            last_value_x, last_value_y = self._value_x, self._value_y
            self._value_x = (touch.x - self.x) * (self.max_x - self.min_x) / float(self.width) + self.min_x
            self._value_y = (touch.y - self.y) * (self.max_y - self.min_y) / float(self.height) + self.min_y
            if self._value_x >= self.max_x:
                self._value_x = self.max_x
            if self._value_x <= self.min_x:
                self._value_x = self.min_x
            if self._value_y >= self.max_y:
                self._value_y = self.max_y
            if self._value_y <= self.min_y:
                self._value_y = self.min_y
            if not self._value_x == last_value_x or not self._value_y == last_value_y:
                self.dispatch_event('on_value_change', self._value_x, self._value_y)
            return True
        return super(MTXYSlider, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
        return super(MTXYSlider, self).on_touch_up(touch)

class MTBoundarySlider(MTWidget):
    '''MTBoundarySlider is a widget that allows you to select minimum and maximum values.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `orientation` : str, default is vertical
            Type of orientation, can be 'horizontal' or 'vertical'
        `value_max` : int, default is `max - (max/4)`
            The default maximum value
        `value_min` : int, the default is `min + (max/4)`
            The default minumum value
        `showtext` : boolean, defaults to false
            If true, the widget will show the min/max value

    :Styles:
        `slider-color` : color
            Color of the slider
        `bg-color` : color
            Background color of the slider

    :Events:
        `on_value_change` (value_min, value_max)
            Fired when min or max is changed
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('showtext', False)
        if kwargs.get('orientation') == 'vertical':
            kwargs.setdefault('size', (30, 400))
        else:
            kwargs.setdefault('size', (400, 30))

        super(MTBoundarySlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts    = [] # only react to touch input that originated on this widget
        self.orientation    = kwargs.get('orientation')
        if self.orientation not in ('horizontal', 'vertical'):
            raise Exception('Invalid orientation %s. Must be horizontal or vertical' % self.orientation)
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')
        self.showtext       = kwargs.get('showtext')

        kwargs.setdefault('value_min', self.min)
        kwargs.setdefault('value_max', self.max)
        self.value_min = kwargs.get('value_min')
        self.value_max = kwargs.get('value_max')

    def set_value(self, name, value):
        if name in ('value_min', 'value_max'):
            if self.orientation == 'vertical':
                x = self.height / self.ratio
            else:
                x = self.width / self.ratio
            if value < 0:
                return self.__setattr__(name, 0)
            if value > x:
                return self.__setattr__(name, x)
        if name == 'value_min' and value > self.value_max:
            return
        if name == 'value_max' and value < self.value_min:
            return
        return self.__setattr__(name, value)

    def get_value(self):
        '''Scale the value to the minimum and maximum system set by the user'''
        if self.orientation == 'vertical':
            tmin = (self.value_min / self.height) * self.max
            tmax = (self.value_max / self.height) * self.max
        elif self.orientation == 'horizontal':
            tmin = (self.value_min / self.width) * self.max
            tmax = (self.value_max / self.width) * self.max
        return tmin, tmax

    def on_value_change(self, vmin, vmax):
        pass

    @property
    def ratio(self):
        if self.orientation == 'vertical':
            return self.height / (self.max - self.min)
        return self.width / (self.max - self.min)

    def draw(self):
        px, py = self.style['padding']
        px2, py2 = px / 2, py / 2
        if self.orientation == 'vertical':
            pos = (self.x + px2, self.y + self.value_min * self.ratio + py2)
            size = (self.width - px, (self.value_max - self.value_min) *
                    self.ratio - py)
            textposmin = (self.x + self.width, self.y + self.value_min * self.ratio)
            textposmax = (self.x + self.width, self.y + self.value_max * self.ratio)
        elif self.orientation == 'horizontal':
            pos = (self.x + self.value_min * self.ratio + px2, self.y + py2)
            size = ((self.value_max - self.value_min) * self.ratio - px,
                    self.height - py)
            textposmin = (self.x + self.value_min * self.ratio, self.y + self.height)
            textposmax = (self.x + self.value_max * self.ratio, self.y + self.height)

        # draw outer rectangle
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

        # draw inner rectangle
        set_color(*self.style.get('slider-color'))
        drawCSSRectangle(pos=pos, size=size, style=self.style, prefix='slider')
        if self.showtext and len(self.touchstarts):
            drawLabel(u'%.1f' % (self.value_min), pos=textposmin, font_size=self.style['font-size'])
            drawLabel(u'%.1f' % (self.value_max), pos=textposmax, font_size=self.style['font-size'])

    def on_touch_down(self, touch):
        # So the first on_touch_move in a
        # two-finger-drag doesn't teleport the widget
        if self.collide_point(touch.x, touch.y):
            if touch.is_double_tap:
                # Randomize the bound
                if self.orientation == 'vertical':
                    self.value_min = random.randrange(0, self.height)
                    self.value_max = random.randrange(self.value_min, self.height)
                else:
                    self.value_min = random.randrange(0, self.width)
                    self.value_max = random.randrange(self.value_min, self.width)
            # Decide wether we will move the upper or lower bound
            if self.orientation == 'vertical':
                if touch.y < (self.value_min * self.ratio + self.y*2 +
                              self.value_max * self.ratio)/2:
                    touch.userdata['boundary.side'] = 'value_min'
                else:
                    touch.userdata['boundary.side'] = 'value_max'
            elif self.orientation == 'horizontal':
                if touch.x < (self.value_min * self.ratio + self.x*2 +
                              self.value_max * self.ratio)/2:
                    touch.userdata['boundary.side'] = 'value_min'
                else:
                    touch.userdata['boundary.side'] = 'value_max'

            self.touchstarts.append(touch.id)
            self.on_touch_move(touch)
            return True
        return super(MTBoundarySlider, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            # Either move a given bound, or shift both
            if self.orientation == 'vertical':
                if len(self.touchstarts) >= 2:
                    # Two or more fingers, shift the whole bound
                    rel = (touch.y - touch.dypos)
                    self.value_min += rel
                    self.value_max += rel
                else:
                    # Only one, just change one bound
                    self.set_value(touch.userdata['boundary.side'],
                                   (touch.y - self.y) / self.ratio)
                    self.dispatch_event('on_value_change', *self.get_value())
            elif self.orientation == 'horizontal':
                if len(self.touchstarts) >= 2:
                    # Two or more fingers, shift the whole bound
                    rel = (touch.x - touch.dxpos)
                    self.value_min += rel
                    self.value_max += rel
                else:
                    # Only one, just change one bound
                    self.set_value(touch.userdata['boundary.side'],
                                   (touch.x - self.x) / self.ratio)
                    self.dispatch_event('on_value_change', *self.get_value())
            return True
        return super(MTBoundarySlider, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
        return super(MTBoundarySlider, self).on_touch_up(touch)

class MTMultiSlider(MTWidget):
    '''Multi slider widget look like an equalizer widget.

    :Parameters:
        `sliders` : int, default to 20
            Number of sliders
        `spacing` : int, default to 1
            Spacing between slider
        `init_value` : float, default to 0.5
            Start value of all sliders

    :Styles:
        `slider-color` : color
            Color of slider
        `bg-color` : color
            Background color of slider

    :Events:
        `on_value_change` (values)
            Fired when the value of one slider change

    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('sliders', 20)
        kwargs.setdefault('size', (400, 300))
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('init_value', 0.5)
        super(MTMultiSlider, self).__init__(**kwargs)

        self.register_event_type('on_value_change')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self._sliders = kwargs.get('sliders')
        self._spacing = kwargs.get('spacing')
        self._init_value = kwargs.get('init_value')
        self.slider_values = [self._init_value for x in range(self._sliders)]

    def _get_sliders(self):
        return self._sliders
    def _set_sliders(self, quantity):
        if quantity < self._sliders:
            self.slider_values = self.slider_values[0:quantity]
            self._sliders = quantity
        if quantity > self._sliders:
            self.slider_values = self.slider_values + list(
                [self._init_value for x in range(quantity - self._sliders)])
            self._sliders = quantity
        else:
            return
    sliders = property(_get_sliders, _set_sliders,
                       doc='Get/set the number of sliders')

    def _get_spacing(self):
        return self._spacing
    def _set_spacing(self, spacing):
        self._spacing = spacing
    spacing = property(_get_spacing, _set_spacing)

    def draw(self):
        # Draw background
        set_color(*self.style.get('bg-color'))
        drawRectangle(pos=self.pos, size=self.size)
        # Draw sliders
        set_color(*self.style.get('slider-color'))
        for slider in range(self._sliders):
            pos_x = self.x + slider * (float(self.width) / self._sliders)
            pos_y = self.y
            size_x = (float(self.width) / self._sliders) - self._spacing
            size_y = self.height * self.slider_values[slider]
            drawRectangle(pos = (pos_x, pos_y), size = (size_x, size_y))

    def on_value_change(self, value):
        pass

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchstarts.append(touch.id)
            self.on_touch_move(touch)
            return True
        return super(MTMultiSlider, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            if touch.x > self.x and touch.x < self.x + self.width:
                current_slider = self.return_slider(touch.x)
                last_value = self.slider_values[current_slider]
                self.slider_values[current_slider] = (touch.y - self.y) / float(self.height)
                if self.slider_values[current_slider] >= 1:
                    self.slider_values[current_slider] = 1
                if self.slider_values[current_slider] <= 0:
                    self.slider_values[current_slider] = 0

                if not self.slider_values[current_slider] == last_value:
                    self.dispatch_event('on_value_change', self.slider_values)
            return True
        return super(MTMultiSlider, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
        return super(MTMultiSlider, self).on_touch_up(touch)

    def return_slider(self, x):
        return int((x - self.x) / float(self.width)  * self._sliders)

