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
    _cache = {}
    def _select_font(self):
        fontsize = int(self.options['font_size'] * 1.333)
        fontname = self.options['font_name'].split(',')[0]
        id = '%s.%s' % (unicode(fontname), unicode(fontsize))
        if not id in self._cache:
            filename = os.path.join(pymt.pymt_data_dir, 'DejaVuSans.ttf')
            font = ImageFont.truetype(filename, fontsize)
            self._cache[id] = font
            print 'LabelPIL add cache', id, font, fontsize

        return self._cache[id]

    def get_extents(self, text):
        font = self._select_font()
        return font.getsize(text)

    def refresh(self):
        width, height = 1, 0
        lines = self.label.split('\n')
        for line in lines:
            w, h = self.get_extents(line)
            print 'line=', line, w, h
            width = max(width, w)
            height += int(h)

        width = int(width)
        height = int(max(height, 1))

        # create a surface, context, font...
        print 'create surface', width, height
        im = PIL.Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(im)

        x, y = 0, 0
        for line in lines:
            w, h = self.get_extents(line)
            print 'linB=', line, w, h
            draw.text((x, y), line, font=self._select_font())
            y += int(h)

        data = pymt.ImageData(width, height,
            im.mode, im.tostring())

        if self.texture is None:
            self.texture = pymt.Texture.create(width, height)
            self.texture.flip_vertical()
        elif width > self.texture.width or height > self.texture.height:
            self.texture = pymt.Texture.create(width, height)
            self.texture.flip_vertical()

        # update texture
        self.texture.blit_data(data)

        super(LabelPIL, self).refresh()

