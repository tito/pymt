# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Wang game !'

from pymt import *
import random
import pyglet
import math

class Bat(MTWidget):
    def __init__(self, va, vb, **kwargs):
        self.va = va
        self.vb = vb
        super(Bat, self).__init__(**kwargs)

    def draw(self):
        set_color(1, 1, 1)
        drawLine([self.va.x, self.va.y, self.vb.x, self.vb.y])

class Ball(MTWidget):
    """ Pong ball that will bounce of walls and paddles """

    def __init__(self, **kwargs):
        super(Ball, self).__init__(**kwargs)
        """ Init position and a random speed. Also ball is not out yet """
        self.dx = random.randint(2, 6)
        self.dy = random.randint(2, 6)
        self.img                 = pyglet.image.load('ball.png')
        self.image          = pyglet.sprite.Sprite(self.img)
        self.image.x        = random.randint(100, 400)
        self.image.y        = random.randint(100, 200)
        self.size           = (100, 100)
        self.h = self.img.height * 0.5
        self.w = self.img.width * 0.5
        
    def draw(self):
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = 0.5
        self.size           = (self.img.width, self.img.height)
        self.image.draw()      
        
    def on_draw(self):
        self.x, self.y = self.x + self.dx, self.y + self.dy        
        if self.y + self.img.height*0.5 >= w.height or self.y <= 0:
            self.dy = -self.dy
        if self.x + self.img.width*0.5 >= w.width or self.x <= 0:
            self.dx = -self.dx
        self.draw()

def collide(a, b): 
    """ Basic rectangle collision """
    if a.y + a.h < b.va.y:
         return False
    if a.y > b.vb.y:
         return False
    if a.x + a.w < b.va.x:
        return False
    if a.x >  b.vb.x:
        return False

    return True    

class Wang(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('mindist', 200)
        super(Wang, self).__init__(**kwargs)
        self.ball = Ball()
        self.add_widget(self.ball)
        self.touchs = {}
        self.bats = []
        self.mindist = kwargs.get('mindist')

        
    def draw(self):
        for b in self.bats:
            b.draw()
            if collide(self.ball, b):
                self.ball.dx = -self.ball.dx + random.randint(0, 4)
                self.ball.dy = -self.ball.dy + random.randint(0, 4)
                # Make sure the ball isn't going too fast
                if self.ball.dx > 6:
                    self.ball.dx = 6

                if self.ball.dx < -6:
                    self.ball.dx = -6

                if self.ball.dy > 6:
                    self.ball.dx > 6
            

    def update_bat(self):
        self.bats = []
        if len(self.touchs) < 2:
            return
        keys = self.touchs.keys()
        for ka in keys:
            va = self.touchs[ka]
            for kb in keys[1:]:
                vb = self.touchs[kb]
                if Vector.distance(va, vb) < self.mindist:
                    self.bats.append(Bat(va, vb))

    def on_touch_down(self, touches, touchID, x, y):
        self.touchs[touchID] = Vector(x, y)
        self.update_bat()

    def on_touch_move(self, touches, touchID, x, y):
        if self.touchs.has_key(touchID):
            self.touchs[touchID] = Vector(x, y)
            self.update_bat()
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.touchs.has_key(touchID):
            del self.touchs[touchID]
            self.update_bat()
            return True


if __name__ == '__main__':
    w = MTWindow()
    w.add_widget(Wang(mindist=200))

    runTouchApp()
