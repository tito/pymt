'''
Label: a simple text label
'''

__all__ = ('MTLabel', )

from pymt.graphx import drawLabel, set_color, drawCSSRectangle, getLabel, getLastLabel
from pymt.ui.widgets.widget import MTWidget

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
        `multiline`: bool, default to False
            If True, the text will be fit inside the width

    MTLabel support all parameters from the Core label. Check 
    :py:class:`~pymt.core.text.LabelBase` class to known all availables
    parameters.
    '''

    # TODO reactivate slots
    #__slots__ = ('autowidth', 'autoheight', 'autosize', 'label',
    #    '_used_label', 'kwargs', 'anchor_x', 'anchor_y')

    def __init__(self, **kwargs):
        kwargs.setdefault('markup', False)
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        kwargs.setdefault('autowidth', False)
        kwargs.setdefault('autoheight', False)
        kwargs.setdefault('autosize', False)
        kwargs.setdefault('label', '')
        kwargs.setdefault('multiline', False)

        self.kwargs = {}

        self.multiline  = kwargs['multiline']
        self.autowidth  = kwargs['autowidth']
        self.autoheight = kwargs['autoheight']
        self.autosize   = kwargs['autosize']
        self.anchor_x   = kwargs['anchor_x']
        self.anchor_y   = kwargs['anchor_y']
        self.label      = kwargs['label']
        del kwargs['autowidth']
        del kwargs['autoheight']
        del kwargs['autosize']
        del kwargs['label']
        del kwargs['multiline']

        super(MTLabel, self).__init__(**kwargs)

        size_specified = 'size' in kwargs or 'width' in kwargs or 'height' in kwargs
        for item in ('size', 'pos'):
            if item in kwargs:
                del kwargs[item]

        if self.multiline:
            kwargs['size'] = (self.width, None)

        self.kwargs = kwargs

        # copy style to inline one (needed for css reloading)
        if 'color' in kwargs:
            self._inline_style['color'] = kwargs['color']
        if 'font_name' in kwargs:
            self._inline_style['font-name'] = kwargs['font_name']
        if 'font_size' in kwargs:
            self._inline_style['font-size'] = kwargs['font_size']
        if 'bold' in kwargs and 'italic' in kwargs and \
            kwargs['bold'] and kwargs['italic']:
            self._inline_style['font-weight'] = 'bolditalic'
        elif 'bold' in kwargs and kwargs['bold']:
            self._inline_style['font-weight'] = 'bold'
        elif 'italic' in kwargs and kwargs['italic']:
            self._inline_style['font-weight'] = 'italic'
        if 'padding' in kwargs:
            self._inline_style['padding'] = kwargs['padding']

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
        s = self.style
        self.color = s['color']
        self.font_name = s['font-name']
        self.font_size = s['font-size']
        self.padding = s['padding']
        self.bold = False
        self.italic = False
        if s['font-weight'] in ('bold', 'bolditalic'):
            self.bold = True
        if s['font-weight'] in ('italic', 'bolditalic'):
            self.italic = True


    @property
    def label_obj(self):
        return self._used_label

    def draw(self):
        self.draw_background()
        self.draw_label()

    def draw_label(self, dx=0, dy=0):
        '''Method to draw the label. Accept dx/dy to be added on label position.
        This can be used to draw shadow for example.'''
        # because the anchor_x/anchor_y is propagated to the drawLabel,
        # we don't care about the internal label size.
        kwargs = self.kwargs
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

        # ensure multiline
        if self.multiline:
            kwargs['size'] = (self.width, None)

        # force autosize
        if self.autosize or self.autowidth or self.autoheight:
            if 'size' in kwargs:
                del kwargs['size']
        else:
            # FIXME: found a way to cache this information
            # and not calculate it every frame.
            w, h = self.size
            px = self._used_label.options['padding_x']
            py = self._used_label.options['padding_y']
            w -= px * 2
            h -= py * 2
            kwargs['viewport_size'] = (w, h)

        w, h = drawLabel(label=self.label, pos=pos, **kwargs)
        self._used_label = getLastLabel()
        self._update_size(w, h)

    def draw_background(self):
        '''Draw the background of the widget'''
        set_color(*self.style['bg-color'])
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

    def _update_size(self, w, h):
        if (self.autoheight and self.autowidth) or self.autosize:
            self.size = (w, h)
        elif self.autoheight:
            self.height = h
        elif self.autowidth:
            self.width = w

    def _get_padding_x(self):
        return self.kwargs['padding_x']
    def _set_padding_x(self, x):
        self.kwargs['padding_x'] = x
    padding_x = property(_get_padding_x, _set_padding_x)

    def _get_padding_y(self):
        return self.kwargs['padding_x']
    def _set_padding_y(self, x):
        self.kwargs['padding_y'] = x
    padding_y = property(_get_padding_y, _set_padding_y)

    def _get_padding(self):
        return self.kwargs['padding']
    def _set_padding(self, x):
        self.kwargs['padding'] = x
    padding = property(_get_padding, _set_padding)

    def _get_font_size(self):
        return self.kwargs['font_size']
    def _set_font_size(self, x):
        self.kwargs['font_size'] = x
    font_size = property(_get_font_size, _set_font_size)

    def _get_font_name(self):
        return self.kwargs['font_name']
    def _set_font_name(self, x):
        self.kwargs['font_name'] = x
    font_name = property(_get_font_name, _set_font_name)

    def _get_bold(self):
        return self.kwargs['bold']
    def _set_bold(self, x):
        self.kwargs['bold'] = x
    bold = property(_get_bold, _set_bold)

    def _get_italic(self):
        return self.kwargs['italic']
    def _set_italic(self, x):
        self.kwargs['italic'] = x
    italic = property(_get_italic, _set_italic)

    def _get_anchor_x(self):
        return self.kwargs['anchor_x']
    def _set_anchor_x(self, x):
        self.kwargs['anchor_x'] = x
    anchor_x = property(_get_anchor_x, _set_anchor_x)

    def _get_anchor_y(self):
        return self.kwargs['anchor_y']
    def _set_anchor_y(self, x):
        self.kwargs['anchor_y'] = x
    anchor_y = property(_get_anchor_y, _set_anchor_y)

    def _get_halign(self):
        return self.kwargs['halign']
    def _set_halign(self, x):
        self.kwargs['halign'] = x
    halign = property(_get_halign, _set_halign)

    def _get_valign(self):
        return self.kwargs['valign']
    def _set_valign(self, x):
        self.kwargs['valign'] = x
    valign = property(_get_valign, _set_valign)

    def _get_color(self):
        return self.kwargs['color']
    def _set_color(self, x):
        self.kwargs['color'] = x
    color = property(_get_color, _set_color)

    def _get_markup(self):
        return self.kwargs['markup']
    def _set_markup(self, x):
        self.kwargs['markup'] = x
    markup = property(_get_markup, _set_markup, doc=
        'If true, a :py:class:`~pymt.core.label.markup.MarkupLabel` will be '
        'used instead of :py:class:`~pymt.core.label.Label`'
    )

    def _get_viewport_pos(self):
        return self.kwargs['viewport_pos']
    def _set_viewport_pos(self, x):
        self.kwargs['viewport_pos'] = x
    viewport_pos = property(_get_viewport_pos, _set_viewport_pos)

    def _get_viewport_size(self):
        return self.kwargs['viewport_size']
    viewport_size = property(_get_viewport_size)
