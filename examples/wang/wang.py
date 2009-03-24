from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Wang game !'

from pymt import *
from pyglet.gl import *
import random
import pyglet
import math
import sys

try:
    from Box2D.Box2D import *
except:
    pymt_logger.critical('You need Box2D to make wang work. You can grab it here : http://code.google.com/p/pybox2d/')
    sys.exit(1)

class Bat(MTWidget):
    def __init__(self, va, vb, **kwargs):
        self.va = va
        self.vb = vb
        super(Bat, self).__init__(**kwargs)
        self.world = self.body = None

    def __del__(self):
        # ensure that body from box2D is freed
        if self.world and self.body:
            self.world.DestroyBody(self.body)

    def setup_physics(self, world):
        # create all physics
        self.world = world
        self.update(self.va, self.vb)

    def update(self, va, vb):
        # destroy old body
        if self.body:
            self.world.DestroyBody(self.body)
            self.body = None

        # create a new body
        # i don't known how we can do without recreate
        # since box2d don't allow to change a shape
        # in run-time.
        self.va = va
        self.vb = vb
        self.bodyDef = b2BodyDef()
        self.bodyDef.position = (0,0)
        self.body = self.world.CreateBody(self.bodyDef)
        self.bodyShape = None
        self.shapeDef = b2EdgeChainDef()
        self.shapeDef.friction = 1
        self.shapeDef.vertices = [self.va, self.vb]
        self.bodyShape = self.body.CreateShape(self.shapeDef)
        self.body.SetMassFromShapes()

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
        self.image      = pyglet.sprite.Sprite(pyglet.image.load('ball.png'))
        self.pos        = random.randint(100, 400), random.randint(100, 200)
        self.owidth     = self.image.width
        self.old_pos    = self.pos

    def setup_physics(self, world):
        # create body
        self.bodyDef = b2BodyDef()
        self.bodyDef.position = self.pos
        self.body = world.CreateBody(self.bodyDef)
        self.shapeDef = b2CircleDef()
        self.shapeDef.radius = self.radius - 2
        self.shapeDef.density = 1
        self.shapeDef.friction = 0
        self.shapeDef.restitution = 2
        # set initial velocity
        velocity = b2Vec2(random.randint(600, 1000), random.randint(600, 1000))
        self.body.SetLinearVelocity(velocity)
        self.body.CreateShape(self.shapeDef)
        self.body.SetMassFromShapes()

    def draw(self):
        # update position
        self.image.x, self.image.y = self.x - self.radius, self.y - self.radius
        self.image.scale           = self.scale
        self.image.draw()

    def on_draw(self):
        # update scale if necessary
        self.scale = (self.radius * 2) / float(self.owidth)
        self.size  = (self.radius * 2, self.radius * 2)
        self.pos = self.body.position.x, self.body.position.y
        self.draw()

class Wang(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('mindist', 200)
        kwargs.setdefault('root', None)
        super(Wang, self).__init__(**kwargs)
        self.touchs = {}
        self.bats = {}
        self.mindist = kwargs.get('mindist')
        self.root = kwargs.get('root')
        self.setup_physics()

        self.ball = Ball(radius=30)
        self.add_widget(self.ball)


    def add_widget(self, widget):
        super(Wang, self).add_widget(widget)
        widget.setup_physics(self.world)

    def setup_physics(self):
        # create bound of world
        self.worldAABB = b2AABB()
        self.worldAABB.lowerBound.Set(-100, -100)
        self.worldAABB.upperBound.Set(self.root.width + 100, self.root.height + 100)
        # no gravity allowed
        self.gravity = (0, 0)
        # permit to sleep
        self.dosleep = True
        # create world
        self.world = b2World(self.worldAABB, self.gravity, self.dosleep)
        self.bodies = []

        # create each border of windows
        cx = self.root.width / 2.0
        cy = self.root.height / 2.0
        for i in range(4):
            if i == 0:
                x, y = cx, 0
                w, h = cx, 1
            elif i == 1:
                x, y = 0, cy
                w, h = 1, cy
            elif i == 2:
                x, y = cx, self.root.height
                w, h = cx, 1
            elif i == 3:
                x, y = self.root.width, cy
                w, h = 1, cy

            # create body for corner
            groundBodyDef = b2BodyDef()
            groundBodyDef.position = x, y
            groundBody = self.world.CreateBody(groundBodyDef)
            groundShapeDef = b2PolygonDef()
            groundShapeDef.density = 1
            groundShapeDef.friction = 0
            groundShapeDef.restitution = 1
            groundShapeDef.SetAsBox(w, h)
            groundBodyShape = groundBody.CreateShape(groundShapeDef)
            self.bodies.append(groundBody)

    def draw(self):
        # step the world !
        velocityIterations = 10
        positionIterations = 8
        self.world.Step(1.0 / 60.0, velocityIterations, positionIterations)

        # draw bats
        for b in self.bats:
            self.bats[b].draw()

    def update_bat(self):
        self.used = ['']
        keys = self.touchs.keys()
        # test every possibilities
        for ka in keys:
            va = self.touchs[ka]
            for kb in keys:
                # same key, abort
                if ka == kb:
                    continue

                # same value, abort
                vb = self.touchs[kb]
                if va == vb:
                    continue

                # if the inverted key exist, abort
                altkey = '%s:%s' % (kb, ka)
                if altkey in self.bats:
                    continue

                # create key
                key = '%s:%s' % (ka, kb)
                if Vector.distance(va, vb) < self.mindist:
                    # record that this bat is used
                    self.used.append(key)

                    # create if not exist
                    if key in self.bats:
                        self.bats[key].update(va, vb)
                    else:
                        bat = Bat(va, vb)
                        bat.setup_physics(self.world)
                        self.bats[key] = bat

        # destroy non-used bat
        for key in difference(self.bats.keys(), self.used):
            del self.bats[key]

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
    w = MTWindow(bgcolor=(0,0,0,0))
    w.add_widget(Wang(mindist=200, root=w))

    runTouchApp()
