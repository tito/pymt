'''
Wang game, by Mathieu Virbel <tito@bankiz.org>
Thanks for Math to sponc game (from libavg.de)
and http://zoonek.free.fr/LaTeX/Triangle/index.shtml

Lot of things can be optimized, it's just a raw version working
after some hours of arithemic.
'''

from pymt import *
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
        self.sprite = Image.load('../wang/ball.png')
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

        for color, line in self.debugline:
            set_color(*color)
            drawLine(line)

    def speedup(self, f):
        if f <= 0:
            return
        self.speed = 100 + min(80 / f, 400)

class MenuItem(MTButton):
    def __init__(self, **kwargs):
        super(MenuItem, self).__init__(**kwargs)
        self.radius = kwargs.get('radius')
        self.color = kwargs.get('color')

    def collide_point(self, x, y):
        w = self.get_parent_window()
        w2 = w.width / 2.
        return Vector(*self.pos).distance(Vector(x, y)) < self.radius

    def draw(self):
        w = self.get_parent_window()
        w2 = w.width / 2.
        self.x = w2
        set_color(*self.color)
        drawCircle(pos=self.pos, radius=self.radius)
        drawCircle(pos=self.pos, radius=self.radius, linewidth=5)
        self.label_obj.x, self.label_obj.y = self.pos
        self.label_obj.draw()


class Menu(MTWidget):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.radius = kwargs.get('radius')
        self.game = kwargs.get('game')
        self.menuitems = []
        self.do_show = False

    def collide_point(self, x, y):
        w = self.get_parent_window()
        w2 = w.width / 2.
        return Vector(w2, 0).distance(Vector(x, y)) < self.radius

    def _press_reset(self, *largs):
        self.game.reset(score=True)

    def _press_speed_add(self, *largs):
        self.game.speed += 1
        if self.game.speed > 10:
            self.game.speed = 10

    def _press_speed_del(self, *largs):
        self.game.speed -= 1
        if self.game.speed < 1:
            self.game.speed = 1

    def _press_ball_add(self, *largs):
        self.game.generate_ball()

    def _press_ball_del(self, *largs):
        self.game.remove_ball()

    def _press_menu(self, *largs):
        self.do_show = not self.do_show
        for c in self.menuitems:
            c.visible = self.do_show
        self.game.pause = self.do_show

    def create_ui(self):
        w = self.get_parent_window()
        w2 = w.width / 2.

        self.menu = MenuItem(color=(.2, .2, .2, .7), radius=40,
                            pos=(w2, 0))
        self.menu.push_handlers(on_press=self._press_menu)
        self.add_widget(self.menu)

        btn = MenuItem(label='Restart', color=(.7, 0, 0, .7),
                       radius=40, pos=(w2, 100), visible=False)
        btn.push_handlers(on_press=self._press_reset)
        self.menuitems.append(btn)
        btn = MenuItem(label='Ball +1', color=(0, .7, 0, .7),
                       radius=40, pos=(w2, 200), visible=False)
        btn.push_handlers(on_press=self._press_ball_add)
        self.menuitems.append(btn)
        btn = MenuItem(label='Ball -1', color=(0, 0, .7, .7),
                       radius=40, pos=(w2, 300), visible=False)
        btn.push_handlers(on_press=self._press_ball_del)
        self.menuitems.append(btn)
        btn = MenuItem(label='Speed +1', color=(0, .7, 0, .7),
                       radius=40, pos=(w2, 400), visible=False)
        btn.push_handlers(on_press=self._press_speed_add)
        self.menuitems.append(btn)
        btn = MenuItem(label='Speed -1', color=(0, 0, .7, .7),
                       radius=40, pos=(w2, 500), visible=False)
        btn.push_handlers(on_press=self._press_speed_del)
        self.menuitems.append(btn)

        for btn in self.menuitems:
            self.add_widget(btn)

    def draw(self):
        if len(self.menuitems) == 0:
            self.create_ui()
        if not self.do_show:
            return
        w = self.get_parent_window()
        w2 = w.width / 3.
        w3 = w.width / 3.
        h2 = w.height / 2.
        self.menu.pos = (w2, 0)
        drawLabel('Speed x%d' % self.game.speed, font_size=42, pos=(w3 - 100, h2 - 50))
        drawLabel('Balls %d' % len(self.game.balls), font_size=42, pos=(w3 - 100, h2))


class Wang(MTWidget):

    BAT_LENGTH_MAX = 350

    def __init__(self, **kwargs):
        super(Wang, self).__init__(**kwargs)
        self.balls = []
        self.balls.append(Ball(pos=(100, 100), game=self))
        for ball in self.balls:
            self.add_widget(ball)

        self.labelA = MTLabel(label='0', font_size=48, autoheight=True)
        self.labelB = MTLabel(label='0', font_size=48, autoheight=True)
        self._scoreA = 0
        self._scoreB = 0
        self.side = 0
        self.pause = False
        self.need_reset = True
        self.speed = 1
        self.menu = Menu(radius=40, game=self)
        self.add_widget(self.menu)

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

    def generate_ball(self):
        if len(self.balls) >= 20:
            return
        ball = Ball(pos=(100, 100), game=self)
        self.balls.append(ball)
        self.add_widget(ball)
        self.reset()

    def remove_ball(self):
        if len(self.balls) < 2:
            return
        ball = self.balls.pop()
        self.remove_widget(ball)
        self.reset()

    def reset(self, score=False):
        self.need_reset = False
        self.bats = []
        self.batsid = []
        if score:
            self.scoreA = 0
            self.scoreB = 0
        self.side = (self.side + 1) % 2
        w = self.get_parent_window()
        for ball in self.balls:
            ball.reset()
            ball.y = w.height / 2.
            if self.side == 0:
                ball.x = w.width / 3.
            else:
                ball.x = (w.width / 3.) * 2.

    def update(self):
        dt = getFrameDt() * self.speed
        if self.pause:
            dt = 0
        w = self.get_parent_window()
        w2 = w.width / 2.

        if self.need_reset:
            self.reset()

        # update bats
        self.bats = []
        self.batsid = []
        touches = getCurrentTouches()
        for a in touches:
            for b in touches[1:]:
                if a == b:
                    continue
                apos = Vector(self.to_widget(*a.pos))
                bpos = Vector(self.to_widget(*b.pos))
                if Vector(apos).distance(bpos) > 400:
                    continue
                aside, bside = 0, 0
                if apos.x > w2:
                    aside = 1
                if bpos.x > w2:
                    bside = 1
                if aside != bside:
                    continue
                if (apos, bpos) in self.batsid:
                    continue
                if (bpos, apos) in self.batsid:
                    continue
                self.bats.append(Bat(a=apos, b=bpos))
                self.batsid.append((apos, bpos))

        for ball in self.balls:
            ball.update(dt)

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
        self.labelA.x = w2 - self.labelA.width - 10
        self.labelA.y = w.height - self.labelA.height - 10
        self.labelB.x = w2 + 10
        self.labelB.y = w.height - self.labelB.height - 10
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
        for ball in self.balls:
            ball.draw()
        for bat in self.bats:
            bat.draw()

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
