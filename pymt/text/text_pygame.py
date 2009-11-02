'''
Text Pygame: Draw text with pygame
'''

__all__ = ('LabelPygame', )

import pymt
from . import LabelBase

try:
    import pygame
except:
    raise

pygame_cache = {}

# init pygame font
pygame.font.init()

class LabelPygame(LabelBase):
    def _get_font_id(self):
        return '|'.join([str(self.options[x]) for x \
            in ('font_size', 'font_name', 'bold', 'italic')])

    def _get_font(self):
        id = self._get_font_id()
        if id not in pygame_cache:
            # try to search the font
            font = pygame.font.match_font(
                self.options['font_name'],
                bold=self.options['bold'],
                italic=self.options['italic'])

            # fontobject
            fontobject = pygame.font.Font(font, self.options['font_size'] * 1.4)
            pygame_cache[id] = fontobject

        return pygame_cache[id]

    def update(self):
        font = self._get_font()

        # don't change antialiased and no background
        # with theses settings, font are always in 32 bits
        surface = font.render(self.label, True, (255, 255, 255))

        data = pymt.ImageData(surface.get_width(), surface.get_height(),
            'RGBA', buffer(surface.get_buffer())[:])

        # create a texture from this data
        # and flip texture in vertical way
        self.texture = pymt.Texture.create_from_data(data)
        self.texture.flip_vertical()

        super(LabelPygame, self).update()


