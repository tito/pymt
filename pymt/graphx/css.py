'''
CSS: Draw shapes with css attributes !
'''

__all__ = ['drawCSSRectangle']

from draw import *
from pyglet.gl import GL_LINE_LOOP

def drawCSSRectangle(pos=(0,0), size=(100,100), style={}, prefix=None):
    '''Draw a rectangle with CSS

    :Styles:
        * border-radius
        * border-radius-precision
        * draw-border
        * draw-alpha-background
        * alpha-background

    '''

    # hack to remove prefix in style
    if prefix is not None:
        prefix += '-'
        newstyle = {}
        for k in style:
            if prefix in k:
                newstyle[k.replace(prefix, '')] = style[k]
        style = newstyle

    style.setdefault('border-radius', 0)
    style.setdefault('border-radius-precision', .1)
    style.setdefault('draw-border', 0)
    style.setdefault('draw-alpha-background', 0)
    style.setdefault('alpha-background', (1, 1, .5, .5))

    k = { 'pos': pos, 'size': size }
    if style['border-radius'] > 0:
        k.update({
            'radius': style['border-radius'],
            'precision': style['border-radius-precision']
        })
        drawRoundedRectangle(**k)
        if style['draw-border']:
            drawRoundedRectangle(style=GL_LINE_LOOP, **k)
        if style['draw-alpha-background']:
            drawRoundedRectangleAlpha(alpha=style['alpha-background'], **k)
    else:
        drawRectangle(**k)
        if style['draw-border']:
            drawRectangle(style=GL_LINE_LOOP, **k)
        if style['draw-alpha-background']:
            drawRectangleAlpha(alpha=style['alpha-background'], **k)

