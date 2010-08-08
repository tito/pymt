'''
CSS: Draw shapes with css attributes !
'''

__all__ = ('drawCSSRectangle', )

import os
from pymt.graphx.draw import drawRectangleAlpha, drawRectangle, \
        drawRoundedRectangle, drawRoundedRectangleAlpha
from pymt.graphx.colors import set_color
from pymt.cache import Cache
from pymt.graphx.statement import GlDisplayList, gx_color
from OpenGL.GL import GL_LINE_BIT, GL_LINE_LOOP, \
        glPushAttrib, glPopAttrib, glLineWidth

if not 'PYMT_DOC' in os.environ:
    Cache.register('pymt.cssrect', limit=100, timeout=60)


def drawCSSRectangle(pos=(0, 0), size=(100, 100), style=dict(), prefix=None, state=None):
    '''Draw a rectangle with CSS
    
    :Parameters:
        `state`: if a certain state string is passed, we will use styles with this postifx instead.
            for example:  style[bg-color] and style[bg-color-down] are both set.
            if state == "down", we wil use bg-color-down instead of bg-color

    :Styles:
        * alpha-background (color)
        * border-radius (float)
        * border-radius-precision (float)
        * border-width (float)
        * draw-alpha-background (bool)
        * draw-background (bool)
        * draw-border (bool)

    '''

    bg_image = style.get('bg-image-'+str(state))
    if not bg_image:
        bg_image = style.get('bg-image')

    # Check if we have a cached version
    cache_id = '%s:%s:%s:%s:%s' % (pos, size, style, prefix, state)
    cache = Cache.get('pymt.cssrect', cache_id)
    if cache:
        cache.draw()
        if bg_image:
            bg_image.size = size
            bg_image.pos = pos
            bg_image.draw()
        return


    # lets use the ones for given state,
    # and ignore the regular ones if the state ones are there
    if state:
        state = "-" + state
        newstyle = {}
        overwrites = []
        for s in style:
            if state in s:
                overwrite  = s.replace(state, '')
                newstyle[overwrite] = style[s]
                overwrites.append(overwrite)
            if s not in overwrites:
                newstyle[s] = style[s]
        style = newstyle

    # hack to remove prefix in style
    if prefix is not None:
        prefix += '-'
        newstyle = {}
        for k in style:
            newstyle[k] = style[k]
        for k in style:
            if prefix in k:
                newstyle[k.replace(prefix, '')] = style[k]
        style = newstyle

    style.setdefault('border-width', 1.5)
    style.setdefault('border-radius', 0)
    style.setdefault('border-radius-precision', .1)
    style.setdefault('draw-border', 0)
    style.setdefault('draw-background', 1)
    style.setdefault('draw-alpha-background', 0)
    style.setdefault('alpha-background', (1, 1, .5, .5))

    k = { 'pos': pos, 'size': size }

    new_cache = GlDisplayList()
    with new_cache:

        if state:
            set_color(*style['bg-color']) #hack becasue old widgets set this themselves

        linewidth = style.get('border-width')

        bordercolor = None
        if 'border-color' in style:
            bordercolor = style['border-color']

        if style['border-radius'] > 0:
            k.update({
                'radius': style['border-radius'],
                'precision': style['border-radius-precision']
            })
            if style['draw-background']:
                drawRoundedRectangle(**k)
            if style['draw-border']:
                if linewidth:
                    glPushAttrib(GL_LINE_BIT)
                    glLineWidth(linewidth)
                if bordercolor:
                    with gx_color(*bordercolor):
                        drawRoundedRectangle(style=GL_LINE_LOOP, **k)
                else:
                    drawRoundedRectangle(style=GL_LINE_LOOP, **k)
                if linewidth:
                    glPopAttrib()
            if style['draw-alpha-background']:
                drawRoundedRectangleAlpha(alpha=style['alpha-background'], **k)
        else:
            if style['draw-background']:
                drawRectangle(**k)
            if style['draw-border']:
                if linewidth:
                    glPushAttrib(GL_LINE_BIT)
                    glLineWidth(linewidth)
                if bordercolor:
                    with gx_color(*bordercolor):
                        drawRectangle(style=GL_LINE_LOOP, **k)
                else:
                    drawRectangle(style=GL_LINE_LOOP, **k)
                if linewidth:
                    glPopAttrib()
            if style['draw-alpha-background']:
                drawRectangleAlpha(alpha=style['alpha-background'], **k)


    # if the drawCSSRectangle is already inside a display list
    # compilation will not happen, but drawing yes.
    # so, store only if a cache is created !
    if new_cache.is_compiled():
        Cache.append('pymt.cssrect', cache_id, new_cache)
        new_cache.draw()

    if bg_image:
        bg_image.size = size
        bg_image.pos = pos
        bg_image.draw()
