'''
Button matrix: a lightweight and optimized grid of buttons
'''

__all__ = ('MTButtonMatrix', )

from OpenGL.GL import glTranslatef
from pymt.graphx import set_color, drawRectangle, gx_matrix
from pymt.ui.widgets.widget import MTWidget

class MTButtonMatrix(MTWidget):
    '''ButtonMatrix is a lightweight Grid of buttons/tiles
      collide_point returns which matrix element was hit
      draw_tile(i,j) draws the  tile @ matrix position (i,j)

    :Parameters:
        `matrix_size` : tuple, default to (3, 3)
            Matrix size
        `border` : int, default to 5
            Size of border
        `buttoncolor` : color, default to (.2, .2, .2, 1)
            Color of background
        `downcolor` : color, default to (0, .5, 1, 1)
            Color when the button is pushed

    :Events:
        `on_value_change` (matrix)
            Returns the whole matrix and a button is touched
        `on_press` (row,column,state)
            Returns the state and cell position of a button when touched
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('matrix_size', (3, 3))
        kwargs.setdefault('border', 5)
        kwargs.setdefault('buttoncolor', (0.5, 0.5, 0.5, 1))
        kwargs.setdefault('downcolor', (0, 0.5, 1, 1))
        super(MTButtonMatrix, self).__init__(**kwargs)

        self.register_event_type('on_value_change')
        self.register_event_type('on_press')

        self._matrix_size = kwargs.get('matrix_size')
        self.border = kwargs.get('border')
        self.buttoncolor = kwargs.get('buttoncolor')
        self.downcolor = kwargs.get('downcolor')
        self.matrix = [[0 for i in range(self._matrix_size[1])]
                       for j in range(self._matrix_size[0])]
        self.last_tile = 0

    def on_press(self, *largs):
        pass

    def on_value_change(self, matrix):
        pass

    def reset(self):
        self.matrix = [[0 for i in range(self._matrix_size[1])]
                       for j in range(self._matrix_size[0])]

    def _get_matrix_size(self):
        return self._matrix_size
    def _set_matrix_size(self, size):
        self._matrix_size = size
        self.matrix = [[0 for i in range(self._matrix_size[1])]
                       for j in range(self._matrix_size[0])]
    matrix_size = property(_get_matrix_size, _set_matrix_size,
                           doc='Return size of matrix')

    def draw_tile(self, i, j):
        if self.matrix[i][j] == 0:
            set_color(*self.buttoncolor)
        if self.matrix[i][j]:
            set_color(*self.downcolor)

        with gx_matrix:
            glTranslatef(self.width / self._matrix_size[0] * i + self.x,
                         self.height / self._matrix_size[1] * j + self.y,
                         0)
            s =  (self.width / self._matrix_size[0] - self.border,
                  self.height / self._matrix_size[1] - self.border)
            drawRectangle(size=s)


    def draw(self):
        for i in range (self._matrix_size[0]):
            for j in range (self._matrix_size[1]):
                self.draw_tile(i, j)


    def collide_point(self, x, y):
        i = (x - self.x)/(self.width/self._matrix_size[0])
        j = (y - self.y)/(self.height/self._matrix_size[1])
        if i >= self._matrix_size[0] or j >= self._matrix_size[1]:
            return False # returns false if the click is not within the widget
        if i < 0 or j < 0:
            return False
        else:
            return (int(i), int(j))

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            i, j = self.collide_point(touch.x, touch.y)
            if self.matrix[i][j]:
                self.matrix[i][j] = 0
            else:
                self.matrix[i][j] = 1
            self.dispatch_event('on_value_change', self.matrix)
            self.dispatch_event('on_press', (i, j, self.matrix[i][j]))
            self.last_tile = (i, j)

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y) != self.last_tile:
           self.on_touch_down(touch)
