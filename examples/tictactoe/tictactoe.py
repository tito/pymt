from pymt import *
from pyglet.gl import *


# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'TicTacToe Game'
PLUGIN_AUTHOR = 'Thomas hansen'
PLUGIN_DESCRIPTION = 'Tic Tac Toe game!'


class TTTGame(MTButtonMatrix):

    def __init__(self,**kwargs):
        super(TTTGame, self).__init__(**kwargs)
        self.player_images = (MTWidget(),MTSvg(filename='cross.svg'),MTSvg(filename='circle.svg') )
        self.player = 1
        self.done = False
        self.testpoint = (0,0)

    def select_area(self,i,j):
            self.matrix[i][j] = self.player
            if self.check_win():
                self.done = True
            else:
                if self.player == 1:
                    self.player = 2
                else:
                    self.player = 1

    def on_resize(self, w, h):
        self._width, self._height = w,h


    def on_touch_down(self, touches, touchID, x, y):
        if self.done:
            return True
        i,j = self.collide_point(int(x),int(y))
        if self.matrix[i][j] == 0:
            self.select_area(i,j)
        else:
            pass

    def draw_tile(self, i, j):
        image = self.player_images[self.matrix[i][j]%3]
        glPushMatrix()
        glTranslatef(self.width/self.matrix_size[0]*i, self.height/self.matrix_size[1]*j,0)

        s =  (self.width/self.matrix_size[0],self.height/self.matrix_size[1])
        if self.matrix[i][j]%3 == 0:
            glColor4f(0.25, 0.25, 0.25,1)
            drawRectangle(pos=(20,20),size=(s[0]-40, s[1]-40))
        if self.matrix[i][j]%3 == 1:
            glColor4f(1,0,0,1)
            drawCircle(pos=(s[0]/2, s[1]/2), radius=s[1]/2)
        if self.matrix[i][j]%3 == 2:
            glColor4f(0,0,1,1)
            drawCircle(pos=(s[0]/2, s[1]/2), radius=s[1]/2)
        if self.matrix[i][j] > 2:
            glColor4f(0,1,0,1)
            drawCircle(pos=(s[0]/2, s[1]/2), radius=s[1]/2)

        sx, sy = s[0]/image.width,  s[1]/image.height
        glScaled(sx,sy,1)
        image.draw()
        glPopMatrix()

    def check_row_win(self, p1, p2, p3):
        if (self.matrix[p1[0]][p1[1]] == self.player and
            self.matrix[p2[0]][p2[1]] == self.player and
            self.matrix[p3[0]][p3[1]] == self.player):
            self.matrix[p1[0]][p1[1]] = self.matrix[p2[0]][p2[1]] = self.matrix[p3[0]][p3[1]] = 3+self.player
            return True
        return False

    def check_win(self):
        if self.check_row_win((0,0),(1,0), (2,0)):
            return True
        if self.check_row_win((0,1),(1,1), (2,1)):
            return True
        if self.check_row_win((0,2),(1,2), (2,2)):
            return True
        if self.check_row_win((0,0),(0,1), (0,2)):
            return True
        if self.check_row_win((1,0),(1,1), (1,2)):
            return True
        if self.check_row_win((2,0),(2,1), (2,2)):
            return True
        if self.check_row_win((0,0),(1,1), (2,2)):
            return True
        return False






def pymt_plugin_activate(w, ctx):
    ctx.game = TTTGame(size=w.size)
    w.add_widget(ctx.game)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.game)

#start the application (inits and shows all windows)
if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
