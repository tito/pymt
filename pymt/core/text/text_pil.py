'''
Text PIL: Draw text with PIL
'''

__all__ = ('LabelPIL', )

try:
    from PIL import Image, ImageFont, ImageDraw
except:
    raise

import pymt
import os
from . import LabelBase

# used for fetching extends before creature image surface
default_font = ImageFont.load_default()

class LabelPIL(LabelBase):
    _cache = {}
    def _select_font(self):
        fontsize = int(self.options['font_size'] * 1.333)
        fontname = self.options['font_name'].split(',')[0]
        id = '%s.%s' % (unicode(fontname), unicode(fontsize))
        if not id in self._cache:
            filename = os.path.join(pymt.pymt_data_dir, 'DejaVuSans.ttf')
            font = ImageFont.truetype(filename, fontsize)
            self._cache[id] = font

        return self._cache[id]

    def get_extents(self, text):
        font = self._select_font()
        w, h = font.getsize(text)
        return w, h

    def _render_begin(self):
        # create a surface, context, font...
        self._pil_im = Image.new('RGBA', self.size)
        self._pil_draw = ImageDraw.Draw(self._pil_im)

    def _render_text(self, text, x, y):
        color = tuple(map(lambda x: int(x * 255), self.options['color']))
        self._pil_draw.text((int(x), int(y)), text, font=self._select_font(), fill=color)

    def _render_end(self):
        data = pymt.ImageData(self.width, self.height,
            self._pil_im.mode, self._pil_im.tostring())

        del self._pil_im
        del self._pil_draw

        return data
