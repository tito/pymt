'''
Text PIL: Draw text with PIL
'''

__all__ = ('LabelPIL', )

import pymt
import os
from . import LabelBase

try:
    import PIL
    import ImageFont
    import ImageDraw
except:
    raise

# used for fetching extends before creature image surface
default_font = ImageFont.load_default()

class LabelPIL(LabelBase):
    __cache = {}
    def _select_font(self):
        fontsize = int(self.options['font_size'] * 1.333)
        fontname = self.options['font_name'].split(',')[0]
        id = '%s.%s' % (unicode(fontname), unicode(fontsize))
        if not id in self.__cache:
            filename = os.path.join(pymt.pymt_data_dir, 'DejaVuSans.ttf')
            font = ImageFont.truetype(filename, fontsize)
            self.__cache[id] = font

        return self.__cache[id]

    def _get_extents(self):
        font = self._select_font()
        return font.getsize(self.label)

    def update(self):
        width, height = self._get_extents()

        width = int(max(width, 1))
        height = int(max(height, 1))

        # create a surface, context, font...
        im = PIL.Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), self.label, font=self._select_font())

        data = pymt.ImageData(im.size[0], im.size[1],
            im.mode, im.tostring())

        self.texture = pymt.Texture.create_from_data(data)
        self.texture.flip_vertical()

        super(LabelPIL, self).update()

