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
    '''Pong ball that will bounce of walls and paddles'''

    def __init__(self, **kwargs):
        '''Init position and a random speed. Also ball is not out yet'''
        kwargs.setdefault('radius', 50)

        super(Ball, self).__init__(**kwargs)

        self.radius     = kwargs.get('radius')
        self.dx         = 200
        self.dy         = 0
        self.image      = pyglet.sprite.Sprite(pyglet.image.load('ball.png'))
        self.pos        = random.randint(100, 400), random.randint(100, 200)
        self.owidth     = self.image.width
        self.old_pos    = self.pos

    def draw(self):
        # update position
        self.image.x, self.image.y = self.x - self.radius, self.y - self.radius
        self.image.scale           = self.scale
        self.image.draw()
        drawLine((self.pos[0], self.pos[1], self.cpos[0], self.cpos[1]))

    def on_draw(self):
        # update scale if necessary
        self.scale = (self.radius * 2) / float(self.owidth)
        self.size  = (self.radius * 2, self.radius * 2)

        if self.y + self.radius >= w.height or self.y - self.radius <= 0:
            self.dy = -self.dy
        if self.x + self.radius >= w.width or self.x - self.radius <= 0:
            self.dx = -self.dx

        self.old_pos = self.pos
        dt = getFrameDt()
        self.pos = self.x + self.dx * dt, self.y + self.dy * dt
        self.cpos = ((Vector(self.pos) - Vector(self.old_pos)).normalize() * self.radius) + Vector(self.old_pos)


        self.draw()

def collide(ball, bat):
    '''2 line collisions'''
    v = Vector.line_intersection(
        ball.old_pos, ball.cpos,
        bat.va, bat.vb
    )
    if not v:
        return None
    if not Vector.in_bbox(v, ball.old_pos, ball.cpos):
        return None
    if not Vector.in_bbox(v, bat.va, bat.vb):
        return None
    return v

class Wang(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('mindist', 200)
        super(Wang, self).__init__(**kwargs)
        self.ball = Ball(radius=30)
        self.add_widget(self.ball)
        self.touchs = {}
        self.bats = []
        self.mindist = kwargs.get('mindist')


    def draw(self):
        for b in self.bats:
            b.draw()
            collide_point = collide(self.ball, b)
            if not collide_point:
                continue
            self.ball.pos = self.ball.old_pos
            angle = Vector.angle(collide_point - Vector(self.ball.old_pos), collide_point - Vector(b.va))
            print 'AVANT', self.ball.dx, self.ball.dy, angle
            angle = - 2 * angle
#            if Vector.dot_vector(Vector(self.ball.old_pos) - collide_point, Vector(b.va) - collide_point) > 0:
 #               angle = - angle
            self.ball.dx, self.ball.dy = Vector(self.ball.dx, self.ball.dy).rotate(angle)
            print 'APRES', self.ball.dx, self.ball.dy, angle
            continue

    def update_bat(self):
        self.bats = []
        if len(self.touchs) < 2:
            return
        keys = self.touchs.keys()
        for ka in keys:
            va = self.touchs[ka]
            for kb in keys:
                vb = self.touchs[kb]
                if va == vb:
                    continue
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
