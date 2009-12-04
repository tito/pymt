'''
Text Cairo: Draw text with cairo
'''

__all__ = ('LabelCairo', )

import pymt
from . import LabelBase

try:
    import cairo
except:
    raise

# used for fetching extends before creature image surface
cairo_default_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
cairo_default_context = cairo.Context(cairo_default_surface)

class LabelCairo(LabelBase):
    def _select_font(self, context):
        italic = cairo.FONT_SLANT_NORMAL
        bold = cairo.FONT_WEIGHT_NORMAL
        fontsize = self.options['font_size'] * 1.333
        fontname = self.options['font_name'].split(',')[0]
        if self.options['bold']:
            bold = cairo.FONT_WEIGHT_BOLD
        if self.options['italic']:
            italic = cairo.FONT_WEIGHT_ITALIC

        context.select_font_face(fontname, italic, bold)
        context.set_font_size(fontsize)
        font_options = context.get_font_options()
        font_options.set_hint_style(cairo.HINT_STYLE_FULL)
        context.set_font_options(font_options)

    def get_extents(self, text):
        self._select_font(cairo_default_context)
        x_bearing, y_bearing, width, height, x_advance, y_advance = cairo_default_context.text_extents(text)
        return width, height

    def _render_begin(self):
        # create a surface, context, font...
        self._cairo_surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, *self.size)
        self._cairo_context = cairo.Context(self._cairo_surface)

        self._select_font(self._cairo_context)
        self._cairo_context.set_source_rgb(1., 1., 1.)

    def _render_text(self, text, x, y):
        '''
        context.move_to(0, height)
        context.move_to(-x_bearing, -y_bearing)
        context.show_text(self.label)
        '''
        self._cairo_context.move_to(x, y)
        self._cairo_context.show_text(text)

    def _render_end(self):
        data = pymt.ImageData(self.width, self.height,
            'RGBA', buffer(self._cairo_surface.get_data())[:])

        self._cairo_surface = None
        self._cairo_context = None

        if self.texture is None:
            self.texture = pymt.Texture.create(*self.size)
            self.texture.flip_vertical()
        elif self.width > self.texture.width or self.height > self.texture.height:
            self.texture = pymt.Texture.create(*self.size)
            self.texture.flip_vertical()

        # update texture
        self.texture.blit_data(data)
