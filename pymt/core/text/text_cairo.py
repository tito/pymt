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

    def _get_extents(self):
        self._select_font(cairo_default_context)
        return cairo_default_context.text_extents(self.label)

    def update(self):
        x_bearing, y_bearing, width, height, x_advance, y_advance = self._get_extents()
        width = int(max(width, 1))
        height = int(max(height, 1))

        # create a surface, context, font...
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)

        self._select_font(context)

        context.move_to(0, height)
        context.move_to(-x_bearing, -y_bearing)

        context.set_source_rgb(1., 1., 1.)

        context.show_text(self.label)

        data = pymt.ImageData(width, height,
            'RGBA', buffer(surface.get_data())[:])

        # create a texture from this data
        # and flip texture in vertical way
        self.texture = pymt.Texture.create_from_data(data)
        self.texture.flip_vertical()

        super(LabelCairo, self).update()

