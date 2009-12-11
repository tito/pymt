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
        return '|'.join([unicode(self.options[x]) for x \
            in ('font_size', 'font_name', 'bold', 'italic')])

    def _get_font(self):
        id = self._get_font_id()
        if id not in pygame_cache:
            # try to search the font
            font = pygame.font.match_font(
                self.options['font_name'].replace(' ', ''),
                bold=self.options['bold'],
                italic=self.options['italic'])

            # fontobject
            fontobject = pygame.font.Font(font,
                            int(self.options['font_size'] * 1.333))
            pygame_cache[id] = fontobject

        return pygame_cache[id]

    def get_extents(self, text):
        font = self._get_font()
        w, h = font.size(text)
        return w, h

    def _render_begin(self):
        # XXX big/little endian ??
        rgba_mask = 0xff000000, 0xff0000, 0xff00, 0xff
        self._pygame_surface = pygame.Surface(self.size, 0, 32, rgba_mask)

    def _render_text(self, text, x, y):
        font = self._get_font()
        text = font.render(text, True, (255, 255, 255))
        self._pygame_surface.blit(text, (x, y), None, pygame.BLEND_RGBA_ADD)

    def _render_end(self):
        data = pymt.ImageData(self.width, self.height,
            'RGBA', buffer(self._pygame_surface.get_buffer())[:])

        del self._pygame_surface

        return data
