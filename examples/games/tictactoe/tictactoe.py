from pymt import *
from OpenGL.GL import *


# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'TicTacToe Game'
PLUGIN_AUTHOR = 'Thomas Hansen + Mathieu Virbel'
PLUGIN_DESCRIPTION = 'Tic Tac Toe game!'

class TTTWinner(MTWidget):
    def __init__(self, **kwargs):
        super(TTTWinner, self).__init__(**kwargs)
        self.game = kwargs.get('game')
        self.text = kwargs.get('text')

    def draw(self):
        set_color(0, 0, 0, .9)
        center=Vector(self.get_parent_window().size)/2
        drawRectangle(pos=(0, center.y-50), size=(self.get_parent_window().width, 100))
        drawLabel(label=self.text, pos=center, font_size=28)

    def on_touch_down(self, *largs):
        self.parent.remove_widget(self)
        self.game.restart()
        return True

    def on_touch_move(self, *largs):
        return True

    def on_touch_up(self, *largs):
        return True

class TTTGame(MTButtonMatrix):

    def __init__(self,**kwargs):
        kwargs.setdefault('matrix_size', (3, 3))
        super(TTTGame, self).__init__(**kwargs)
        self.player_images = (MTWidget(),MTSvg(filename='cross.svg'),MTSvg(filename='circle.svg') )
        self.player = 1
        self.done = False
        self.testpoint = (0,0)

    def restart(self):
        self.done = False
        self.player = 1
        self.testpoint = (0, 0)
        self.reset()

    def show_winner(self, text):
        popup = TTTWinner(game=self, text=text)
        self.get_parent_window().add_widget(popup)

    def select_area(self,i,j):
        self.matrix[i][j] = self.player
        winner = self.check_win()
        if winner is not None:
            self.done = True
            self.show_winner("WINNER !")
        elif self.check_full():
            self.done = True
            self.show_winner("GAME OVER :(")
        else:
            if self.player == 1:
                self.player = 2
            else:
                self.player = 1

    def on_resize(self, w, h):
        self._width, self._height = w,h

    def on_touch_down(self, touch):
        if self.done:
            return True
        i,j = self.collide_point(int(touch.x),int(touch.y))
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
            set_color(0.25, 0.25, 0.25)
            drawRectangle(pos=(20,20),size=(s[0]-40, s[1]-40))
        if self.matrix[i][j]%3 == 1:
            set_color(1,0,0)
            drawCircle(pos=(s[0]/2, s[1]/2), radius=s[1]/2)
        if self.matrix[i][j]%3 == 2:
            set_color(0,0,1)
            drawCircle(pos=(s[0]/2, s[1]/2), radius=s[1]/2)
        if self.matrix[i][j] > 2:
            set_color(0,1,0)
            drawCircle(pos=(s[0]/2, s[1]/2), radius=s[1]/2)

        sx, sy = s[0]/image.width,  s[1]/image.height
        set_color(1, 1, 1, .99)
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
            return (0, 0)
        if self.check_row_win((0,1),(1,1), (2,1)):
            return (0, 1)
        if self.check_row_win((0,2),(1,2), (2,2)):
            return (0, 2)
        if self.check_row_win((0,0),(0,1), (0,2)):
            return (0, 0)
        if self.check_row_win((1,0),(1,1), (1,2)):
            return (1, 0)
        if self.check_row_win((2,0),(2,1), (2,2)):
            return (2, 0)
        if self.check_row_win((0,0),(1,1), (2,2)):
            return (0, 0)
        if self.check_row_win((2,0),(1,1), (0,2)):
            return (0, 0)
        return None

    def check_full(self):
        full = 0
        for x in range(0, self.matrix_size[0]):
            for y in range(0, self.matrix_size[1]):
                if self.matrix[x][y] == 0:
                    full += 1
        if full == 0:
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
