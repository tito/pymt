'''
Label: a simple text label
'''


__all__ = ['MTLabel']

import pymt
from ...graphx import drawLabel, set_color, drawCSSRectangle, getLabel, getLastLabel
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTLabel(MTWidget):
    '''A simple label ::

        label = MTLabel(label='Plop world')

    :Parameters:
        `autosize`: bool, default to False
            Update size information with label size
        `autowidth`: bool, default to False
            Update width information with the label content width
        `autoheight`: bool, default to False
            Update height information with the label content height

    MTLabel support all parameters from the Core label. Check `LabelBase`
    class to known all availables parameters.
    '''
    __slots__ = ('autowidth', 'autoheight', 'autosize', 'label',
        '_used_label', 'kwargs', 'anchor_x', 'anchor_y')

    def __init__(self, **kwargs):
        kwargs.setdefault('markup', False)
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        kwargs.setdefault('autowidth', False)
        kwargs.setdefault('autoheight', False)
        kwargs.setdefault('autosize', False)
        kwargs.setdefault('label', '')

        self.autowidth  = kwargs.get('autowidth')
        self.autoheight = kwargs.get('autoheight')
        self.autosize   = kwargs.get('autosize')
        self.anchor_x   = kwargs.get('anchor_x')
        self.anchor_y   = kwargs.get('anchor_y')
        self.label      = kwargs.get('label')
        del kwargs['autowidth']
        del kwargs['autoheight']
        del kwargs['autosize']
        del kwargs['label']

        self.kwargs = {}

        super(MTLabel, self).__init__(**kwargs)

        size_specified = 'size' in kwargs or 'width' in kwargs or 'height' in kwargs
        for item in ('size', 'pos'):
            if item in kwargs:
                del kwargs[item]

        self.kwargs = kwargs

        # copy style to inline one (needed for css reloading)
        if 'color' in kwargs:
            self._inline_style['color'] = kwargs.get('color')
        if 'font-name' in kwargs:
            self._inline_style['font-name'] = kwargs.get('font-name')
        if 'font-size' in kwargs:
            self._inline_style['font-size'] = kwargs.get('font-size')
        if 'bold' in kwargs and 'italic' in kwargs and \
            kwargs.get('bold') and kwargs.get('italic'):
            self._inline_style['font-weight'] = 'bolditalic'
        elif 'bold' in kwargs and kwargs.get('bold'):
            self._inline_style['font-weight'] = 'bold'
        elif 'italic' in kwargs and kwargs.get('italic'):
            self._inline_style['font-weight'] = 'italic'

        # update from inline
        self.apply_css(self._inline_style)

        # update this label size
        label = getLabel(label=self.label, **kwargs)
        if not size_specified:
            self.size = label.size
        self._update_size(*label.size)
        self._used_label = label

    def apply_css(self, styles):
        super(MTLabel, self).apply_css(styles)

        # transform css attribute to style one
        k = self.kwargs
        s = self.style
        k['color'] = s['color']
        k['font_name'] = s['font-name']
        k['font_size'] = s['font-size']
        k['bold'] = False
        k['italic'] = False
        if s['font-weight'] in ('bold', 'bolditalic'):
            k['bold'] = True
        if s['font-weight'] in ('italic', 'bolditalic'):
            k['italic'] = True


    @property
    def label_obj(self):
        return self._used_label

    def draw(self):
        if not self.visible:
            return
        self.draw_background()
        self.draw_label()

    def draw_label(self, dx=0, dy=0):
        '''Method to draw the label. Accept dx/dy to be added on label position.
        This can be used to draw shadow for example.'''
        # because the anchor_x/anchor_y is propagated to the drawLabel,
        # we don't care about the internal label size.
        pos = list(self.center)
        if self.anchor_x == 'left':
            pos[0] = self.x
        elif self.anchor_x == 'right':
            pos[0] = self.x + self.width
        if self.anchor_y == 'top':
            pos[1] = self.y + self.height
        elif self.anchor_y == 'bottom':
            pos[1] = self.y

        pos[0] += dx
        pos[1] += dy

        # force autosize
        if self.autosize or self.autowidth or self.autoheight:
            if 'size' in self.kwargs:
                del self.kwargs['size']

        w, h = drawLabel(label=self.label, pos=pos, **self.kwargs)
        self._used_label = getLastLabel()
        self._update_size(w, h)

    def draw_background(self):
        '''Draw the background of the widget'''
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

    def _update_size(self, w, h):
        if (self.autoheight and self.autowidth) or self.autosize:
            self.size = (w, h)
        elif self.autoheight:
            self.height = h
        elif self.autowidth:
            self.width = w

    def __getattribute__(self, name):
        try:
            return super(MTLabel, self).__getattribute__(name)
        except:
            kw = self.kwargs
            if name in kw:
                return kw[name]
            raise

    def __setattr__(self, name, value):
        try:
            kw = super(MTLabel, self).__getattribute__('kwargs')
            if name in ('font_size', 'font_name', 'bold', 'italic', 'size',
                        'anchor_x', 'anchor_y', 'halign', 'valign', 'padding',
                        'padding_x', 'padding_y', 'color'):
                kw[name] = value
        except:
            pass
        return super(MTLabel, self).__setattr__(name, value)

MTWidgetFactory.register('MTLabel', MTLabel)
