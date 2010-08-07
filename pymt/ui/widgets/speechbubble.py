'''
Speech Bubble: a little speech bubble !
'''

__all__ = ('MTSpeechBubble', )

from pymt.ui.widgets.label import MTLabel
from pymt.graphx import drawPolygon, drawRoundedRectangle, gx_matrix
from pymt.vector import Vector
from OpenGL.GL import GL_LINE_SMOOTH, GL_LINE_LOOP, \
    glEnable, glTranslatef, glLineWidth

class MTSpeechBubble(MTLabel):
    '''A little speed bubble !

    :Parameters:
        `multiline` : bool, default to True
            Make label multiline
        `bgcolor` : list, default to (183./255, 224./255, 1)
            Background color of bubble
        `bordercolor` : list, default to (1, 1, 1)
            Border color of bubble
        `bordersize` : int, default to 2
            Size of border
        `radius` : int, default to 8
            Size of radius box
        `padding` : int, default to 5
            Padding inside label
        `relpos` : list, default to (-30, 20)
            Relative position of the bubble
        `trisize` : int, default to 8
            Size of triangle
    	`trirelpos` : list, default to (0, 0)
            Relative position of the triangle
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('multiline', True)
        kwargs.setdefault('bgcolor', (183./255, 224./255, 1))
        kwargs.setdefault('bordercolor', (1, 1, 1))
        kwargs.setdefault('bordersize', 2)
        kwargs.setdefault('radius', 8)
        kwargs.setdefault('padding', 5)
        kwargs.setdefault('autoheight', True)
        kwargs.setdefault('relpos', (-30, 20))
        kwargs.setdefault('trisize', 8)
        kwargs.setdefault('trirelpos', (0, 0))
        super(MTSpeechBubble, self).__init__(**kwargs)
        self.bordercolor    = kwargs.get('bordercolor')
        self.bordersize     = kwargs.get('bordersize')
        self.bgcolor        = kwargs.get('bgcolor')
        self.padding        = kwargs.get('padding')
        self.radius         = kwargs.get('radius')
        self.autoheight     = kwargs.get('autoheight')
        self.relpos         = kwargs.get('relpos')
        self.trisize        = kwargs.get('trisize')
        self.trirelpos      = kwargs.get('trirelpos')

    def draw(self):

        # extract relative position
        rx, ry = self.relpos

        # calculate triangle
        mx = self.x + rx + self.width * 0.5 + self.trirelpos[0]
        my = self.y + ry + self.height * 0.5 + self.trirelpos[1]
        angle = Vector(1, 0).angle(Vector(mx - self.x, my - self.y))
        vpos = Vector(mx, my)
        v1 = Vector(self.trisize, 0).rotate(angle) + vpos
        v2 = Vector(-self.trisize, 0).rotate(angle) + vpos

        # draw border
        if self.bordersize > 0:
            drawRoundedRectangle(
                pos=(self.x - self.padding - self.bordersize + rx,
                     self.y - self.padding - self.bordersize + ry),
                size=(self.width + self.padding * 2 + self.bordersize * 2,
                      self.height + self.padding * 2 + self.bordersize * 2),
                radius=self.radius,
                color=self.bordercolor
            )

            glEnable(GL_LINE_SMOOTH)
            glLineWidth(self.bordersize * 2)
            drawPolygon((self.x, self.y, v1.x, v1.y, v2.x, v2.y), style=GL_LINE_LOOP)

        # draw background
        drawRoundedRectangle(
            pos=(self.x - self.padding + rx,
                 self.y - self.padding + ry),
            size=(self.width + self.padding * 2,
                  self.height + self.padding * 2),
            radius=self.radius,
            color=self.bgcolor
        )
        drawPolygon((self.x, self.y, v1.x, v1.y, v2.x, v2.y))

        # hack to translate label position
        with gx_matrix:
            glTranslatef(rx, ry, 0)
            super(MTSpeechBubble, self).draw()

if __name__ == '__main__':
    from pymt import runTouchApp
    bl = MTSpeechBubble(
        color=(0,0,0,1),
        label="Bubble"
    )
    bl.pos = (100, 100)
    runTouchApp(bl)
