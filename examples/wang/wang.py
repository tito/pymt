'''
Wang game, by Mathieu Virbel <tito@bankiz.org>
Thanks for Math to sponc game (from libavg.de)
and http://zoonek.free.fr/LaTeX/Triangle/index.shtml

Lot of things can be optimized, it's just a raw version working
after some hours of arithemic.
'''

from pymt import *
import pyglet
from copy import copy
import random
import math

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Wang game'
PLUGIN_AUTHOR = 'Mathieu Virbel'
PLUGIN_DESCRIPTION = 'Play on Pong with multitouch !'


def in_between(val, b1, b2):
    return ((b1 >= val and val >= b2) or (b1 <= val and val <= b2))

def angle(o, a1, a2):
    return (a1 - o).angle(a2 - o)

def perp(l, m):
    P, Q = l.points
    pa = P.y - Q.y
    pb = Q.x - P.x
    pc = P.x * (Q.y-P.y) - P.y * (Q.x-P.x)
    za = -pb
    zb = copy(pa)
    zc = pb * m.x - pa * m.y
    if zb == 0:
        return
    return Line(Vector(200, -(za * 200 + zc) / zb),
                Vector(100, -(za * 100 + zc) / zb))

class Line(object):
    def __init__(self, p1, p2):
        self.points = (p1, p2)

    def get_angle(self):
        v = self.points[1] - self.points[0]
        angle = math.atan2(v.x, v.y)
        if angle < 0:
            angle += math.pi * 2.
        return angle

    def get_normal(self):
        return self.get_angle() + math.pi / 2.

    def collide(self, line):
        a = self.points[0].x
        b = self.points[0].y
        c = self.points[1].x - a
        d = self.points[1].y - b
        e = line.points[0].x
        f = line.points[0].y
        g = line.points[1].x - e
        h = line.points[1].y - f

        dem = g * d - c * h
        if dem == 0: # parallel 
            return False

        s = (a * d + f * c - b * c - e * d) / dem
        x = e + s * g
        y = f + s * h
        return Vector(x, y)

    def clash(self, line):
        ka, kb = self.points
        la, lb = line.points

        p = self.collide(line)
        if not p:
            return False

        if in_between(p.x, ka.x, kb.x) and \
           in_between(p.x, la.x, lb.x) and \
           in_between(p.y, ka.y, kb.y) and \
           in_between(p.y, la.y, lb.y):
            return p

        return False

    def length(self):
        ka, kb = self.points
        return ka.distance(kb)

    def is_hard(self):
        return True

    def on_clash(self, object, position):
        if self.is_hard():
            object.dobounce(self)
        return False

    def in_between(self, p):
        ka, kb = self.points
        return in_between(p.x, ka.x, kb.x) and in_between(p.y, ka.y, kb.y)


class Bat(MTWidget):
    def __init__(self, **kwargs):
        super(Bat, self).__init__(**kwargs)
        self.bpos = (0, 0)
        self.a = Vector(kwargs.get('a'))
        self.b = Vector(kwargs.get('b'))

    def _get_a(self):
        return Vector(self.pos)
    def _set_a(self, value):
        self.pos = value
    a = property(_get_a, _set_a)

    def _get_b(self):
        return Vector(self.bpos)
    def _set_b(self, value):
        self.bpos = value
    b = property(_get_b, _set_b)

    def _get_line(self):
        return Line(self.a, self.b)
    line = property(_get_line)

    def draw(self):
        set_color(1, 1, 1)
        drawLine((self.a.x, self.a.y, self.b.x, self.b.y), width=5.)


class Ball(MTWidget):
    def __init__(self, **kwargs):
        super(Ball, self).__init__(**kwargs)
        self.game = kwargs.get('game')
        self.debugline = []
        self.debug = False
        img = pyglet.image.load('../wang/ball.png')
        self.sprite = pyglet.sprite.Sprite(img)
        self.reset()

    def reset(self):
        self.radius = 30
        self.speed = 150
        self.v = Vector(random.random() * 2 - 1,
                        random.random() * 2 - 1).normalize()

    def update(self, dt):
        w = self.get_parent_window()
        pos = Vector(*self.pos)
        dir = self.v * dt * self.speed
        next = pos + dir
        bline = Line(pos, next)

        if self.debug:
            self.debugline = []

        for bat in self.game.bats:

            # search perpendicular line
            p = Vector(*next)
            l = perp(bat.line, p)
            if not l:
                continue

            # get the collision point between bat and perpendicular
            cl = bat.line.collide(l)
            if not cl:
                continue

            # if the collision point is on bat, go !
            if not bat.line.in_between(cl):
                continue

            # DEBUG: show the perpendicular line.
            if self.debug:
                self.debugline.append(((0, 0, 1), [cl.x, cl.y, p.x, p.y]))

            # get the collision point between bat and direction
            c = bat.line.collide(bline)
            if not c:
                return

            # DEBUG: draw the direction vector
            if self.debug:
                self.debugline.append(((0, 1, 0), [c.x, c.y, p.x, p.y]))

            # prepare rotation of direction
            rot = angle(p, cl, c)
            rot = 180 + 2 * rot

            # DEBUG: show the future direction vector
            if self.debug:
                v = self.v.rotate(rot).normalize() * self.radius * 2
                self.debugline.append(((1, 0, 0), [p.x + v.x, p.y + v.y, p.x, p.y]))

            # if distance between perpendicular collision point
            # and bat is < radius, we got a collision
            dist = cl.distance(p)
            if dist > self.radius:
                continue

            # speedup ?
            self.speedup(bat.line.length() / Wang.BAT_LENGTH_MAX)

            # rotate direction.
            self.v = self.v.rotate(rot)

            # new next
            dir = self.v * dt * self.speed
            next = pos + dir

        # bounds
        if next.x < -self.radius:
            self.game.winB()
        if next.x > w.width + self.radius:
            self.game.winA()
        if next.y < self.radius:
            next.y = self.radius
            self.v.y = -self.v.y
        if next.y > w.height - self.radius:
            next.y = w.height - self.radius
            self.v.y = -self.v.y

        self.pos = next

    def draw(self):
        set_color(1, 1, 1)
        self.sprite.x = self.x - self.sprite.width / 2.
        self.sprite.y = self.y - self.sprite.height / 2.
        self.sprite.draw()
        '''
        set_color(.3, .3, .3, .7)
        drawCircle(pos=self.pos, radius=self.radius)
        set_color(1, 1, 1)
        drawCircle(pos=self.pos, radius=self.radius, linewidth=5)
        '''

        for color, line in self.debugline:
            set_color(*color)
            drawLine(line)

    def speedup(self, f):
        if f <= 0:
            return
        self.speed = 100 + min(80 / f, 400)


class Wang(MTWidget):

    BAT_LENGTH_MAX = 350

    def __init__(self, **kwargs):
        super(Wang, self).__init__(**kwargs)
        self.ball = Ball(pos=(100, 100), game=self)
        self.add_widget(self.ball)
        self.labelA = MTLabel(label='0', font_size=48, autoheight=True)
        self.labelB = MTLabel(label='0', font_size=48, autoheight=True)
        self._scoreA = 0
        self._scoreB = 0
        self.side = 0
        self.need_reset = True

    def _get_scoreA(self):
        return self._scoreA
    def _get_scoreB(self):
        return self._scoreB
    def _set_scoreA(self, value):
        self._scoreA = value
        self.labelA.label = str(value)
    def _set_scoreB(self, value):
        self._scoreB = value
        self.labelB.label = str(value)
    scoreA = property(_get_scoreA, _set_scoreA)
    scoreB = property(_get_scoreB, _set_scoreB)

    def reset(self):
        self.need_reset = False
        self.bats = []
        self.batsid = []
        self.side = (self.side + 1) % 2
        self.ball.reset()
        w = self.get_parent_window()
        self.ball.y = w.height / 2.
        if self.side == 0:
            self.ball.x = w.width / 3.
        else:
            self.ball.x = (w.width / 3.) * 2.

    def update(self):
        dt = getFrameDt() * 2
        w = self.get_parent_window()
        w2 = w.width / 2.

        if self.need_reset:
            self.reset()

        # update bats
        self.bats = []
        self.batsid = []
        touches = getAvailableTouchs()
        for a in touches:
            for b in touches[1:]:
                if a == b:
                    continue
                if Vector(a.pos).distance(b.pos) > 400:
                    continue
                aside, bside = 0, 0
                if a.x > w2:
                    aside = 1
                if b.x > w2:
                    bside = 1
                if aside != bside:
                    continue
                if (a.pos, b.pos) in self.batsid:
                    continue
                if (b.pos, a.pos) in self.batsid:
                    continue
                self.bats.append(Bat(a=a.pos, b=b.pos))
                self.batsid.append((a.pos, b.pos))

        self.ball.update(dt)

    def drawUI(self):
        w = self.get_parent_window()
        w2 = w.width / 2.
        s = w.height / 20.

        # middle line
        set_color(1, 1, 1)
        for x in xrange(0, w.height, int(s * 2)):
            drawLine([w2, x, w2, x + s], width=5)

        # top / bottom line
        drawLine([0, 0, w.width, 0], width=5)
        drawLine([0, w.height, w.width, w.height], width=5)

        # draw scores
        self.labelA.x = w2 - self.labelA.label_obj.content_width - 10
        self.labelA.y = w.height - self.labelA.label_obj.content_height - 10
        self.labelB.x = w2 + 10
        self.labelB.y = w.height - self.labelB.label_obj.content_height - 10
        self.labelA.draw()
        self.labelB.draw()

    def winA(self):
        self.scoreA += 1
        self.need_reset = True

    def winB(self):
        self.scoreB += 1
        self.need_reset = True

    def draw(self):
        self.update()
        self.drawUI()

        # draw
        self.ball.draw()
        for b in self.bats:
            b.draw()

def pymt_plugin_activate(w, ctx):
    ctx.wang = Wang()
    w.add_widget(ctx.wang)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.wang)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
