'''
CSS: Draw shapes with css attributes !
'''

__all__ = ['drawCSSRectangle']

import os
from draw import *
from pymt.cache import Cache
from statement import GlDisplayList
from OpenGL.GL import *


if not 'PYMT_DOC' in os.environ:
    Cache.register('css_rect', limit=100, timeout=5)
def drawCSSRectangle(pos=(0,0), size=(100,100), style={}, prefix=None):
    '''Draw a rectangle with CSS

    :Styles:
        * border-radius
        * border-radius-precision
        * draw-border
        * draw-alpha-background
        * alpha-background

    '''
    # Check if we have a cached version
    cache_id = '%s:%s:%s:%s' % (pos, size, style, prefix)
    cache = Cache.get('css_rect', cache_id)
    if cache:
        cache.draw()
        return

    # hack to remove prefix in style
    if prefix is not None:
        prefix += '-'
        newstyle = {}
        for k in style:
            if prefix in k:
                newstyle[k.replace(prefix, '')] = style[k]
        style = newstyle

    style.setdefault('border-width', 1.5)
    style.setdefault('border-radius', 0)
    style.setdefault('border-radius-precision', .1)
    style.setdefault('draw-border', 0)
    style.setdefault('draw-alpha-background', 0)
    style.setdefault('alpha-background', (1, 1, .5, .5))

    k = { 'pos': pos, 'size': size }

    new_cache = GlDisplayList()
    with new_cache:

        linewidth = None
        old_linewidth = glGetIntegerv(GL_ALIASED_LINE_WIDTH_RANGE)[1]
        if style.get('border-width') != old_linewidth:
            linewidth = style.get('border-width')
        del style['border-width']

        if style['border-radius'] > 0:
            k.update({
                'radius': style['border-radius'],
                'precision': style['border-radius-precision']
            })
            if style['draw-background']:
                drawRoundedRectangle(**k)
            if style['draw-border']:
                if linewidth:
                    glLineWidth(linewidth)
                drawRoundedRectangle(style=GL_LINE_LOOP, **k)
                if linewidth:
                    glLineWidth(old_linewidth)
            if style['draw-alpha-background']:
                drawRoundedRectangleAlpha(alpha=style['alpha-background'], **k)
        else:
            if style['draw-background']:
                drawRectangle(**k)
            if style['draw-border']:
                if linewidth:
                    glLineWidth(linewidth)
                drawRectangle(style=GL_LINE_LOOP, **k)
                if linewidth:
                    glLineWidth(old_linewidth)
            if style['draw-alpha-background']:
                drawRectangleAlpha(alpha=style['alpha-background'], **k)

    # if the drawCSSRectangle is already inside a display list
    # compilation will not happen, but drawing yes.
    # so, store only if a cache is created !
    if new_cache.is_compiled():
        Cache.append('css_rect', cache_id, new_cache)
        new_cache.draw()

