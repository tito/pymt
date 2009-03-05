from __future__ import with_statement
__all__ = ['MTButtonMatrix']

from pyglet.gl import *
from ...graphx import set_color, drawRectangle, gx_matrix
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTButtonMatrix(MTWidget):
    '''ButtonMatrix is a lightweight Grid of buttons/tiles
      collide_point returns which matrix element was hit
      draw_tile(i,j) draws the  tile @ matrix position (i,j)
    '''

    def __init__(self,**kwargs):
        kwargs.setdefault('matrix_size', (3,3))
        kwargs.setdefault('border', 5)
        super(MTButtonMatrix, self).__init__(**kwargs)
        self._matrix_size = kwargs.get('matrix_size')
        self.border = kwargs.get('border')
        self.matrix = [[0 for i in range(self._matrix_size[1])] for j in range(self._matrix_size[0])]
        
    def _get_matrix_size(self):
        return self._matrix_size
    def _set_matrix_size(self, size):
        self._matrix_size = size
        self.matrix = [[0 for i in range(self._matrix_size[1])] for j in range(self._matrix_size[0])]
    matrix_size = property(_get_matrix_size,_set_matrix_size)

    def draw_tile(self, i, j):
        if self.matrix[i][j] == 0:
            set_color(1,1,0,1)
        if self.matrix[i][j] == 'down':
            set_color(0,0,1,1)

        with gx_matrix:
            glTranslatef(self.width/self._matrix_size[0]*i, self.height/self._matrix_size[1]*j,0)
            s =  (self.width/self._matrix_size[0]-self.border,self.height/self._matrix_size[1]-self.border)
            drawRectangle(size=s)


    def draw(self):
        for i in range (self._matrix_size[0]):
            for j in range (self._matrix_size[1]):
                self.draw_tile(i,j)


    def collide_point(self, x, y):
        i = x/(self.width/self._matrix_size[0])
        j = y/(self.height/self._matrix_size[1])
        if i >= self._matrix_size[0] or j >= self._matrix_size[1]:
            return False # returns false if the click is not within the widget
        else:
            return (i,j)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            i,j = self.collide_point(x,y)
            if self.matrix[i][j] == 'down':
                self.matrix[i][j] = 0
            else:
                self.matrix[i][j] = 'down'

MTWidgetFactory.register('MTButtonMatrix', MTButtonMatrix)
