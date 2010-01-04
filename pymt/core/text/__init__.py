'''
Text: Handle drawing of text
'''

__all__ = ('LabelBase', 'Label')

import pymt
from .. import core_select_lib
from ...baseobject import BaseObject

DEFAULT_FONT = 'Liberation Sans,Bitstream Vera Sans,Free Sans,Arial, Sans'

class LabelBase(BaseObject):
    __slots__ = ('options', 'texture', '_label', 'color')

    _cache_glyphs = {}

    def __init__(self, label, **kwargs):
        kwargs.setdefault('font_size', 12)
        kwargs.setdefault('font_name', DEFAULT_FONT)
        kwargs.setdefault('bold', False)
        kwargs.setdefault('italic', False)
        kwargs.setdefault('size', (None, None))
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        kwargs.setdefault('halign', 'left')
        kwargs.setdefault('valign', 'bottom')
        kwargs.setdefault('color', (1, 1, 1, 1))

        super(LabelBase, self).__init__(**kwargs)

        self._label     = None

        self.color      = kwargs.get('color')
        self.usersize   = kwargs.get('size')
        self.options    = kwargs
        self.texture    = None
        self.label      = label

    def get_extents(self, text):
        '''Return a tuple with (width, height) for a text.'''
        return (0, 0)

    def _render_begin(self):
        pass

    def _render_text(self, text, x, y):
        pass

    def _render_end(self):
        pass

    def render(self, real=False):
        '''Return a tuple(width, height) to create the image
        with the user constraints.

        2 differents methods are used:
          * if user don't set width, splitting line
            and calculate max width + height
          * if user set a width, blit per glyph
        '''

        uw, uh = self.usersize
        w, h = 0, 0
        x, y = 0, 0
        if real:
            self._render_begin()

        # no width specified, faster method
        if uw is None:
            for line in self.label.split('\n'):
                lw, lh = self.get_extents(line)
                if real:
                    x = 0
                    if self.options['halign'] == 'center':
                        x = int((self.width - lw) / 2.)
                    elif self.options['halign'] == 'right':
                        x = int(self.width - lw)
                    self._render_text(line, x, y)
                    y += int(lh)
                else:
                    w = max(w, int(lw))
                    h += int(lh)

        # constraint
        else:
            # precalculate id/name
            if not self.fontid in self._cache_glyphs:
                self._cache_glyphs[self.fontid] = {}
            cache = self._cache_glyphs[self.fontid]

            if not real:
                # verify that each glyph have size
                glyphs = list(set(self.label))
                for glyph in glyphs:
                    if not glyph in cache:
                        cache[glyph] = self.get_extents(glyph)

            # first, split lines
            glyphs = []
            lines = []
            mw = mh = 0
            for glyph in self.label:
                lw, lh = cache[glyph]

                # get the maximum height for this line
                mh = max(lh, mh)

                # get new line char ?
                # or is the char can fit in the current line ?
                if glyph == '\n' or x + lw > uw:

                    # push a new line with dimensions + glyphs
                    lines.append(((mw, mh), glyphs))
                    glyphs = []

                    # reset size
                    mw = mh = 0

                    # new line ? don't render !
                    if glyph == '\n':
                        continue

                # advance the width
                mw += lw
                glyphs.append(glyph)

            # got some char left ?
            if mw != 0:
                lines.append(((mw, mh), glyphs))

            if not real:
                h = sum([size[1] for size, glyphs in lines])
                w = uw
            else:
                # really render now.
                y = 0
                for size, glyphs in lines:
                    x = 0
                    if self.options['halign'] == 'center':
                        x = int((self.width - size[0]) / 2.)
                    elif self.options['halign'] == 'right':
                        x = int(self.width - size[0])
                    for glyph in glyphs:
                        lw, lh = cache[glyph]
                        self._render_text(glyph, x, y)
                        x += lw
                    y += size[1]

        if not real:
            # was only the first pass
            # return with/height
            w = int(max(w, 1))
            h = int(max(h, 1))
            return w, h

        # get data from provider
        data = self._render_end()
        assert(data)

        # create texture is necessary
        if self.texture is None:
            self.texture = pymt.Texture.create(*self.size)
            self.texture.flip_vertical()
        elif self.width > self.texture.width or self.height > self.texture.height:
            self.texture = pymt.Texture.create(*self.size)
            self.texture.flip_vertical()
        else:
            self.texture = self.texture.get_region(0, 0, self.width, self.height)

        # update texture
        self.texture.blit_data(data)


    def refresh(self):
        # first pass, calculating width/height
        self.size = self.render()
        # second pass, render for real
        self.render(real=True)

    def draw(self):
        if self.texture is None:
            return

        x, y = self.pos
        w, h = self.size
        anchor_x = self.options['anchor_x']
        anchor_y = self.options['anchor_y']

        if anchor_x == 'left':
            pass
        elif anchor_x in ('center', 'middle'):
            x -= w * 0.5
        elif anchor_x == 'right':
            x -= w

        if anchor_y == 'bottom':
            pass
        elif anchor_y in ('center', 'middle'):
            y -= h * 0.5
        elif anchor_y == 'top':
            y -= h

        pymt.set_color(*self.color, blend=True)
        pymt.drawTexturedRectangle(
            texture=self.texture,
            pos=(int(x), int(y)), size=self.texture.size)

    def _get_label(self):
        return self._label
    def _set_label(self, label):
        if label == self._label:
            return
        self._label = unicode(label)
        self.refresh()
    label = property(_get_label, _set_label)
    text = property(_get_label, _set_label)

    @property
    def content_width(self):
        '''Return the content width'''
        if self.texture is None:
            return 0
        return self.texture.width

    @property
    def content_height(self):
        '''Return the content height'''
        if self.texture is None:
            return 0
        return self.texture.height

    @property
    def content_size(self):
        '''Return the content size (width, height)'''
        if self.texture is None:
            return (0, 0)
        return self.texture.size

    @property
    def fontid(self):
        '''Return an uniq id for all font parameters'''
        return str([self.options[x] for x in (
            'font_size', 'font_name', 'bold', 'italic')])

# Load the appropriate provider
Label = core_select_lib('text', (
    ('pygame', 'text_pygame', 'LabelPygame'),
    ('cairo', 'text_cairo', 'LabelCairo'),
    ('pil', 'text_pil', 'LabelPIL'),
))

