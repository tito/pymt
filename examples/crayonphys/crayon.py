from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = False #only turn to true when it's fully functional :)
PLUGIN_TITLE = 'Crayon Physics'
PLUGIN_AUTHOR = 'Riley Dutton'
PLUGIN_DESCRIPTION = 'A simple crayon physics game, with multi-touch!'

from pymt import *
from pyglet.gl import *
import random
import pyglet
import math
import sys

try:
    from Box2D.Box2D import *
except:
    pymt_logger.critical('You need PyBox2D to make Crayon Physics work. You can grab it here : http://code.google.com/p/pybox2d/')
    sys.exit(1)

#Set debugbox below to true to see actual boxes...
debugbox = False

#Set how large the borders around the screen should be.
bordersize = 20

class Shape(MTDragable):
    def __init__(self, coords):
        self.points = []
        self.localpoints = []
        self.startx = coords[0]
        self.starty = coords[1]
        self.color = (random.random(), random.random(), random.random(), 1.0)
        self.complete = False
        self.moving = False
        self.oldx = 0
        self.oldy = 0

        super(Shape, self).__init__(pos=(self.startx, self.starty), size=(50, 50))

    def addpoint(self, coords):
        self.points.append(coords)

    def draw(self):

        #Draw a box around the back of the object for debugging purposes.
        if debugbox:
            glColor4f(1.0, 0.0, 1.0, 1.0)
            pointlist = []
            pointlist.append(self.x)
            pointlist.append(self.y)
            pointlist.append(self.x)
            pointlist.append(self.y + self.height)
            pointlist.append(self.x + self.width)
            pointlist.append(self.y + self.height)
            pointlist.append(self.x + self.width)
            pointlist.append(self.y)
            pyglet.graphics.draw(4, GL_POLYGON, ('v2f', pointlist))

        
        glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        if self.complete:
            pointlist = []
            for point in self.localpoints:
                pointlist.append(point[0] + self.pos[0])
                pointlist.append(point[1] + self.pos[1])
            pyglet.graphics.draw(len(self.points), GL_POLYGON, ('v2f', pointlist))
            #graphx.draw.drawPolygon(pointlist, style=5)
        else: 
             if len(self.points) > 1:
                    pointlist = []
                    for point in self.points:
                        pointlist.append(point[0])
                        pointlist.append(point[1]) 
                    pyglet.graphics.draw(len(self.points), GL_LINE_STRIP, ('v2f', pointlist))
                    

    def finish(self, coords):
        #Check to see how far the final point is from the start point.
        finalpointx = coords[0]
        finalpointy = coords[1]
        distx = abs(finalpointx - self.startx)
        disty = abs(finalpointy - self.starty)
        totaldist = distx + disty
        if totaldist > 75 or len(self.points) < 25:
            return False
        else:
            self.complete = True
            xlist = []
            ylist = []
            for point in self.points:
                xlist.append(point[0])
                ylist.append(point[1])
            #Determine the lowest X value.
            xlist.sort()
            minx = xlist[0]
            #Determine the highest X value.
            xlist.sort(reverse=True)
            maxx = xlist[0]
            #Determine the lowest Y value.
            ylist.sort()
            miny = ylist[0]
            #Determine the highest Y value.
            ylist.sort(reverse=True)
            maxy = ylist[0]

            #Convert our list of points to a *local* list of points.
            for point in self.points:
                self.localpoints.append((point[0] - minx, point[1] - miny))

            # SELF.X, SELF.Y = BOTTOM-LEFT = MINX, MINY
            # WIDTH = MAX - MINX, MAXY - MINY
            self.pos = (minx, miny)
            self.size = (maxx - minx, maxy - miny)
            return True

    def on_draw(self):
        if self.complete and not self.moving:
            self.pos = self.body.position.x - self.width/2, self.body.position.y - self.height/2 #Update our position based on the position of our physics body. Offset it accordingly, as well.
        self.draw()
        
    def setup_physics(self, world):
        # create body
        self.bodyDef = b2BodyDef()
        self.bodyDef.position = (self.pos[0] + self.width/2, self.pos[1] + self.height/2) #Note that the position must be offset, since the Body2D engine treats 0,0 as the center of the object, whereas PyMT treats 0,0 as the bottom-left corner.
        self.body = world.CreateBody(self.bodyDef)
        self.shapeDef = b2PolygonDef()
        hx = self.width/2.0 # half-width
        hy = self.height/2.0 # half-height
        self.shapeDef.SetAsBox(hx, hy)
        self.shapeDef.density = 1
        self.shapeDef.friction = 0.0
        self.shapeDef.restitution = 0.75
        # set initial velocity
        #velocity = b2Vec2(random.randint(-100, 100), random.randint(-100, 100))
        #self.body.SetLinearVelocity(velocity)
        self.body.CreateShape(self.shapeDef)
        self.body.SetMassFromShapes()
        
    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x, y) and not self.parent.jointmode:
            self.moving = True
            self.oldx = self.x
            self.oldy = self.y
            super(Shape, self).on_touch_down(touches, touchID, x, y)

    def on_touch_move(self, touches, touchID, x, y):
        if self.collide_point(x, y) and not self.parent.jointmode:
            super(Shape, self).on_touch_move(touches, touchID, x, y)
            self.body.position = (self.pos[0] + self.width/2, self.pos[1] + self.height/2)
           

    def on_touch_up(self, touches, touchID, x, y):
        if self.collide_point(x, y):
            if self.parent.jointmode:
                self.parent.secondjoint = self.body.GetWorldCenter()
                self.parent.secondjointobj = self
                self.parent.createjoint()
            #Check to see if this is a double-tap...
            elif touches[touchID].is_double_tap:
                #Turn on "create joint mode" -- the first joint point is where we just tapped.
                self.parent.jointmode = True
                self.parent.firstjointobj = self
                self.parent.firstjoint = self.body.GetWorldCenter()
            else:
                super(Shape, self).on_touch_up(touches, touchID, x, y)
                if self.moving:
                    self.body.position = (self.pos[0] + self.width/2, self.pos[1] + self.height/2)
                    #Figure out which way we moved, and how quickly. Set the velocity of the object accordingly.
                    dtx = self.x - self.oldx
                    dty = self.y - self.oldy
                    velocity = b2Vec2(dtx, dty)
                    self.body.SetLinearVelocity(velocity)
                    self.body.ApplyImpulse(b2Vec2(1, 0), (0, 0)) #This gets the body "re-moving" again if it has been stopped.
                    self.moving = False

class StaticShape(MTWidget):
    def __init__(self, pos, size, color):
        self.color = color

        super(StaticShape, self).__init__(pos=pos, size=size)

    def draw(self):
            glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
            pointlist = []
            pointlist.append(self.x)
            pointlist.append(self.y)
            pointlist.append(self.x)
            pointlist.append(self.y + self.height)
            pointlist.append(self.x + self.width)
            pointlist.append(self.y + self.height)
            pointlist.append(self.x + self.width)
            pointlist.append(self.y)
            pyglet.graphics.draw(4, GL_POLYGON, ('v2f', pointlist))

    def on_draw(self):
        self.pos = self.body.position.x - self.width/2, self.body.position.y - self.height/2 #Update our position based on the position of our physics body. Offset it accordingly, as well.
        self.draw()
        
    def setup_physics(self, world):
        groundBodyDef = b2BodyDef()
        groundBodyDef.position = self.x + self.width/2, self.y + self.height/2
        self.body = world.CreateBody(groundBodyDef)
        groundShapeDef = b2PolygonDef()
        groundShapeDef.density = 1
        groundShapeDef.friction = 0
        groundShapeDef.restitution = 1
        groundShapeDef.SetAsBox(self.width/2, self.height/2)
        groundBodyShape = self.body.CreateShape(groundShapeDef)

    def on_touch_up(self, touches, touchID, x, y):
        if self.collide_point(x, y):
            if self.parent.jointmode:
                self.parent.secondjoint = (x, y)
                self.parent.secondjointobj = self
                self.parent.createjoint()
            #Check to see if this is a double-tap...
            elif touches[touchID].is_double_tap:
                #Turn on "create joint mode" -- the first joint point is where we just tapped.
                self.parent.jointmode = True
                self.parent.firstjointobj = self
                self.parent.firstjoint = (x, y)
            
class PhysicsWorld(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('root', None)
        super(PhysicsWorld, self).__init__(**kwargs)
        self.shapes = {}
        self.root = kwargs.get('root')
        self.setup_physics()

        self.jointmode = False
        self.firstjoint = (0, 0)
        self.secondjoint = (0, 0)
        self.firstjointobj = None
        self.secondjointobj = None
        self.joints = []

    def add_widget(self, widget):
        super(PhysicsWorld, self).add_widget(widget)
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
        for i in range(4):
            if i == 0:
                x, y = 0, 0
                w, h = self.root.width, bordersize
            elif i == 1:
                x, y = 0, self.root.height - bordersize
                w, h = self.root.width, bordersize
            elif i == 2:
                x, y = 0, 0
                w, h = bordersize, self.root.height
            elif i == 3:
                x, y = self.root.width - bordersize, 0
                w, h = bordersize, self.root.height
            print x, y, w, h
            groundBody = StaticShape((x, y), (w, h), (0.10, 0.00, 0.00, 1.0))
            self.add_widget(groundBody)
            self.bodies.append(groundBody)

    def draw(self):
        # step the world, unless in joint mode!
        if not self.jointmode:
            velocityIterations = 10
            positionIterations = 8
            self.world.Step(1.0 / 20.0, velocityIterations, positionIterations)


        #Draw our ground/borders.
        for shape in self.bodies:
            shape.on_draw()
        #self.root.clear()
        for shape in self.shapes:
           self.shapes[shape].on_draw()

        #Draw all of our joints.
        for joint in self.joints:
            graphx.set_brush("brush.png", 10)
            graphx.set_color(1.0, 0.0, 1.0, 1.0)
            anchor1 = joint.GetAnchor1().tuple()
            anchor2 = joint.GetAnchor2().tuple()
            points = [anchor1[0], anchor1[1], anchor2[0], anchor2[1]]
            graphx.paintLine(points)

    def createjoint(self):
        jointDef = b2DistanceJointDef()
        jointDef.Initialize(self.firstjointobj.body, self.secondjointobj.body, self.firstjoint, self.secondjoint)
        jointDef.collideConnected = True
        newjoint = self.world.CreateJoint(jointDef).getAsType()
        self.joints.append(newjoint)
        self.jointmode = False
        self.firstjointobj.moving = False
        self.secondjointobj.moving = False


    def on_touch_down(self, touches, touchID, x, y):
        newshape = Shape((x, y))
        self.shapes[touchID] = newshape
        super(PhysicsWorld, self).on_touch_down(touches, touchID, x, y)

    def on_touch_move(self, touches, touchID, x, y):
        self.shapes[touchID].addpoint((x, y))
        super(PhysicsWorld, self).on_touch_move(touches, touchID, x, y)

    def on_touch_up(self, touches, touchID, x, y):
        if self.shapes[touchID].finish((x, y)) == True:
            self.add_widget(self.shapes[touchID])
        del self.shapes[touchID]
        super(PhysicsWorld, self).on_touch_up(touches, touchID, x, y)

def pymt_plugin_activate(root, ctx):
    ctx.world = PhysicsWorld(root=root)
    root.add_widget(ctx.world)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.world)

if __name__ == '__main__':
    w = MTWallpaperWindow(wallpaper="papyrus.jpg", position=MTWallpaperWindow.REPEAT)
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
