#!/usr/bin/env python

import sys

from pyglet import *
from pyglet.gl import *
from mtpyglet import TouchWindow
from graphx import *
from math import *
from pyglet.window import key
from mtpyglet import *
from pyglet.text import HTMLLabel, Label
from math import sqrt, sin
from vector import Vector
from xml.dom import minidom, Node

_id_2_widget = {}

def getWidgetByID(id):
    global _id_2_widget
    if _id_2_widget.has_key(id):
        return _id_2_widget[id]


class AnimationAlpha(object):
    """Collection of animation function, to be used with Animation object."""
    @staticmethod
    def ramp(value_from, value_to, length, frame):
        return (1.0 - frame / length) * value_from  +  frame / length * value_to

    @staticmethod
    def sin(value_from, value_to, length, frame):
        return math.sin(math.pi / 2 * (1.0 - frame / length)) * value_from  + \
            math.sin(math.pi / 2  * (frame / length)) * value_to

    @staticmethod
    def bubble(value_from, value_to, length, frame):
        s = -math.pi / 2
        p = math.pi
        return math.sin(s + p * (1.0 - frame / length)) * value_from  + \
            math.sin(s + p  * (frame / length)) * value_to


class Animation(object):
    """Class to animate property over the time"""
    def __init__(self, widget, label, prop, to, timestep, length,
                 func=AnimationAlpha.ramp):
        self.widget     = widget
        self.frame      = 0.0
        self.prop       = prop
        self.value_to   = to
        self.value_from = self.get_value_from()
        self.timestep   = timestep
        self.length     = length
        self.label      = label
        self.func       = func

    def get_current_value(self):
        return self.func(self.value_from, self.value_to,
                         self.length, self.frame)

    def start(self):
        self.reset()
        pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
        self.widget.dispatch_event('on_animation_start', self)

    def reset(self):
        self.value_from = self.get_value_from()
        self.frame = 0.0
        self.widget.dispatch_event('on_animation_reset', self)

    def advance_frame(self, dt):
        self.frame += self.timestep
        self.set_value_from(self.get_current_value())
        if self.frame < self.length:
            pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
        else:
            self.widget.dispatch_event('on_animation_complete', self)

    def get_value_from(self):
        if hasattr(self.widget, self.prop):
            return self.widget.__getattribute__(self.prop)
        return self.widget.__dict__[self.prop]

    def set_value_from(self, value):
        if hasattr(self.widget, self.prop):
            self.widget.__setattr__(self.prop, value)
        else:
            self.widget.__dict__[self.prop] = value


class MTWidgetFactory(object):
    _widgets = {}

    @staticmethod
    def register(widgetname, widgetclass):
        if not MTWidgetFactory._widgets.has_key(widgetname):
            MTWidgetFactory._widgets[widgetname] = widgetclass

    @staticmethod
    def get(widgetname):
        if MTWidgetFactory._widgets.has_key(widgetname):
            return MTWidgetFactory._widgets[widgetname]
        raise Exception('Widget %s are not known in MTWidgetFactory' % widgetname)

class MTWidget(pyglet.event.EventDispatcher):
    """Global base for any multitouch widget.
    Implement event for mouse, object, touch and animation.

    Event are dispatched through widget only if it's visible.
    """

    def __init__(self, parent=None, **kargs):
        global _id_2_widget
        if kargs.has_key('id'):
            self.id = kargs['id']
            _id_2_widget[kargs['id']] = self

        pyglet.event.EventDispatcher.__init__(self)
        self.parent = parent
        self.children = []
        self._visible = False

        self.animations = []
        self.visible = True
        self.init()

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self.update_event_registration()
    def _get_visible(self):
        return self._visible
    visible = property(_get_visible, _set_visible)

    def update_event_registration(self):
        evs = [ 'on_draw',
                'on_mouse_press',
                'on_mouse_drag',
                'on_mouse_release',
                'on_touch_up',
                'on_touch_move',
                'on_touch_down',
                'on_object_up',
                'on_object_move',
                'on_object_down',
                'on_animation_complete',
                'on_animation_reset',
                'on_animation_start' ]

        if self.visible:
            for ev in evs:
                self.register_event_type(ev)
        else:
            for ev in evs:
                if not hasattr(self, 'event_types'):
                    continue
                if ev in self.event_types:
                    self.event_types.remove(ev)

    def init(self):
        pass

    def bring_to_front(self):
        #remove it from wherever it is and add it back at the top
        if self.parent:
            self.parent.children.remove(self)
            self.parent.children.append(self)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def on_draw(self):
        if not self.visible:
            return
        for w in self.children:
            w.dispatch_event('on_draw')
        self.draw()

    def draw(self):
        pass

    def add_widget(self, w, front=True):
        if front:
            self.children.append(w)
        else:
            self.children.insert(0,w)
        try:
            w.parent = self
        except:
            pass

    def remove_widget(self, w):
        try:
            self.children.remove(w)
        except:
            pass

    def add_animation(self, label, prop, to , timestep, length,
                      func=AnimationAlpha.ramp):
        anim = Animation(self, label, prop, to, timestep, length, func=func)
        self.animations.append(anim)
        return anim

    def start_animations(self, label='all'):
        for anim in self.animations:
            if anim.label == label or label == 'all':
                anim.reset()
                anim.start()


    #hack for now to allow consumtion of events..really we need to work out a different way of propagatiing the events, rather than dispatching for each child
    def consumes_event(self, x,y):
        return False

    def on_touch_down(self, touches, touchID, x, y):
        for w in reversed(self.children):
            w.dispatch_event('on_touch_down', touches, touchID, x, y)
            if w.consumes_event(x,y): break

    def on_touch_move(self, touches, touchID, x, y):
        for w in reversed(self.children):
            w.dispatch_event('on_touch_move', touches, touchID, x, y)
            if w.consumes_event(x,y): break

    def on_touch_up(self, touches, touchID, x, y):
        for w in reversed(self.children):
            w.dispatch_event('on_touch_up', touches, touchID, x, y)
            if w.consumes_event(x,y): break

    def on_mouse_press(self, x, y, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_press',x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_drag',x, y, dx, dy, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_object_down(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_down', touches, touchID,id, x, y,angle)

    def on_object_move(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_move', touches, touchID,id, x, y,angle)

    def on_object_up(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_up', touches, touchID,id, x, y,angle)


class MTWindow(TouchWindow):
    """MTWindow is a window widget who use MTSimulator
       for generating touch event with mouse.
       Use MTWindow as main window application.
    """
    def __init__(self, view=None, fullscreen=False, config=None, color=(.3,.3,.3,1.0)):
        self.color = color
        self.root = MTWidget()

        self.root.parent = self
        if view:
            self.root.add_widget(view)

        self.sim = MTSimulator(self)
        self.root.add_widget(self.sim)

        try:
            if not config:
                config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=1)
                TouchWindow.__init__(self, config)
        except:
            TouchWindow.__init__(self)
            if fullscreen:
                self.set_fullscreen()





    def add_widget(self, w):
        self.root.add_widget(w)
        self.sim.bring_to_front()
    def on_draw(self):
        glClearColor(*self.color)
        self.clear()
        self.root.dispatch_event('on_draw')
        self.sim.draw()

    def on_touch_down(self, touches, touchID, x, y):
        self.root.dispatch_event('on_touch_down', touches, touchID, x, y)

    def on_touch_move(self, touches, touchID, x, y):
        self.root.dispatch_event('on_touch_move', touches, touchID, x, y)

    def on_touch_up(self, touches, touchID, x, y):
        self.root.dispatch_event('on_touch_up', touches, touchID, x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.root.dispatch_event('on_mouse_press', x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.root.dispatch_event('on_mouse_drag', x, y, dx, dy, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.root.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_object_down(self, touches, touchID, id, x, y,angle):
        self.root.dispatch_event('on_object_down', touches, touchID, id, x, y,angle)

    def on_object_move(self, touches, touchID, id, x, y,angle):
        self.root.dispatch_event('on_object_move', touches, touchID, id, x, y,angle)

    def on_object_up(self, touches, touchID, id, x, y,angle):
        self.root.dispatch_event('on_object_up', touches, touchID, id, x, y,angle)


class MTDisplay(MTWidget):
    """MTDisplay is a widget that draw a circle under every touch on window"""
    def __init__(self, parent=None, color=(1.0, 1.0, 1.0, 0.4), radius=10, **kargs):
        MTWidget.__init__(self, parent)
        self.touches    = {}
        self.color      = color
        self.radius     = radius

    def draw(self):
        glColor4f(*self.color)
        for id in self.touches:
            drawCircle(pos=self.touches[id], radius=self.radius)

    def on_touch_down(self, touches, touchID, x, y):
        self.touches[touchID] = (x,y)

    def on_touch_move(self, touches, touchID, x, y):
        self.touches[touchID] = (x,y)

    def on_touch_up(self, touches, touchID, x, y):
        del self.touches[touchID]


class MTContainer(MTWidget):
    """MTContainer is a base for container multiple MTWidget."""
    def __init__(self, children=[], parent=None, layers=1):
        MTWidget.__init__(self, parent)
        self.parent	= parent
        self.layers	= []
        self.obj	= []
        for i in range(layers):
            self.layers.append([])
        for c in children:
            self.add_widget(c)

    def add_widget(self, w, z=0, type='cur'):
        if type not in ['cur', 'obj']:
            return
        if type == 'cur':
            self.layers[z].append(w)
        elif type == 'obj':
            self.obj.append(w)
        try:
            w.parent = self
        except:
            pass

    def on_draw(self):
        if not self.visible:
            return
        for l in self.obj:
            l.draw()
        for l in self.layers:
            for w in l:
                w.on_draw()

    def on_touch_down(self, touches, touchID, x, y):
        for l in self.layers:
            for w in reversed(l):
                if w.dispatch_event('on_touch_down', touches, touchID, x, y):
                    break

    def on_touch_move(self, touches, touchID, x, y):
        for l in self.layers:
            for w in reversed(l):
                if w.dispatch_event('on_touch_move', touches, touchID, x, y):
                    break

    def on_touch_up(self, touches, touchID, x, y):
        for l in self.layers:
            for w in reversed(l):
                if w.dispatch_event('on_touch_up', touches, touchID, x, y):
                    break

    def on_object_down(self, touches, touchID,id, x, y,angle):
        for l in self.obj:
            if l.dispatch_event('on_object_down', touches, touchID,id, x, y,angle):
                break

    def on_object_move(self, touches, touchID,id, x, y,angle):
        for l in self.obj:
            if l.dispatch_event('on_object_move', touches, touchID,id, x, y,angle):
                break

    def on_object_up(self, touches, touchID,id, x, y,angle):
        for l in self.obj:
            if l.dispatch_event('on_object_up', touches, touchID,id, x, y,angle):
                break


class MTRectangularWidget(MTWidget):
    """MTRectangularWidget is a MTWidget with a background color, position and dimension"""
    def __init__(self, parent=None, pos=(0, 0), size=(100, 100), color=(0.6, 0.6, 0.6, 1.0), **kargs):
        MTWidget.__init__(self,parent, **kargs)
        self._x, self._y = pos
        self._width, self._height = size
        self._color = color

        self.register_event_type('on_resize')
        self.register_event_type('on_move')

    def draw(self):
        glColor4d(*self.color)
        drawRectangle((self.x, self.y), (self.width, self.height))

    def consumes_event(self, x,y):
        return self.collidePoint(x,y)

    def collidePoint(self, x, y):
        if( x > self.x  and x < self.x + self.width and
           y > self.y and y < self.y + self.height  ):
            return True


    def on_resize(self, w, h):
        pass

    def on_move(self, x, y):
        pass

    def _set_x(self, x):
        self._x = x
        self.dispatch_event('on_move', self._x, self._y)
    def _get_x(self):
        return self._x
    x = property(_get_x, _set_x)

    def _set_y(self, y):
        self._y = y
        self.dispatch_event('on_move', self._x, self._y)
    def _get_y(self):
        return self._y
    y = property(_get_y, _set_y)

    def _set_width(self, w):
        self._width = w
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_width(self):
        return self._width
    width = property(_get_width, _set_width)

    def _set_height(self, h):
        self._height = h
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_height(self):
        return self._height
    height = property(_get_height, _set_height)


    def _get_center(self):
        return (self._x + self._width/2, self._y+self._height/2)
    def _set_center(self, center):
        self._x = pos[0] - self.width/2
        self._y = pos[1] - self.height/2
        self.dispatch_event('on_move', self._x, self._y)
    center = property(_get_center, _set_center)

    def _set_pos(self, pos):
        self._x, self._y = pos
        self.dispatch_event('on_move', self._x, self._y)
    def _get_pos(self):
        return (self._x, self._y)
    pos = property(_get_pos, _set_pos)

    def _set_size(self, size):
        self.width, self.height = size
        self.dispatch_event('on_resize', self.width, self.height)
    def _get_size(self):
        return (self.width, self.height)
    size = property(_get_size, _set_size)


    def setColor(self, r,g,b, a=1.0):
        self.color = (r,b,g,a)
    def _get_color(self):
        return self._color
    def _set_color(self, col):
        if len(col) == 3:
            self._color = (col[0], col[1], col[2], 1.0)
        if len(col) == 4:
            self._color = col
    color = property(_get_color, _set_color)


class MTDragableWidget(MTRectangularWidget):
    """MTDragableWidget is a moveable widget over the window"""
    def __init__(self, parent=None, pos=(0,0), size=(100,100), **kargs):
        MTRectangularWidget.__init__(self,parent, pos, size, **kargs)
        self.state = ('normal', None)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collidePoint(x,y):
            self.state = ('dragging', touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[0] == 'dragging' and self.state[1] == touchID:
            self.x, self.y = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
            self.state = ('dragging', touchID, x, y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID:
            self.state = ('normal', None)
            return True

class MTButton(MTRectangularWidget):
    """MTButton is a button implementation using MTRectangularWidget"""
    def __init__(self, parent=None, pos=(0, 0), size=(100, 100), label='Button', **kargs):
        MTRectangularWidget.__init__(self,parent, pos, size, **kargs)
        self.register_event_type('on_click')
        self.state          = ('normal', 0)
        self.clickActions   = []
        self.label_obj      = Label(font_size=10, bold=True, )
        self.label_obj.anchor_x = 'center'
        self.label_obj.anchor_y = 'center'        
        self.label          = str(label)

    def get_label(self):
        return self._label
    def set_label(self, text):
        self._label = str(text)
        self.label_obj.text = self.label
    label = property(get_label, set_label)

    def draw(self):
        if self.state[0] == 'down':
            glColor4f(0.5,0.5,0.5,0.5)
            drawRectangle((self.x,self.y) , (self.width, self.height))
        else:
            glColor4f(*self.color)
            drawRectangle((self.x,self.y) , (self.width, self.height))

        self.label_obj.x, self.label_obj.y = self.x +self.width/2 , self.y + +self.height/2
        self.label_obj.draw()

    def on_touch_down(self, touches, touchID, x, y):
        if self.collidePoint(x,y):
            self.state = ('down', touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[1] == touchID and not self.collidePoint(x,y):
            self.state = ('normal', 0)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID and self.collidePoint(x,y):
            self.state = ('normal', 0)
            self.dispatch_event('on_click', touchID, x,y)
            return True


class MTImageButton(MTButton):
    """MTImageButton is a enhanced MTButton that draw an image instead of a text"""
    def __init__(self, image_file, parent=None, pos=(0,0), size=(1,1), scale = 1.0, **kargs):
        MTButton.__init__(self,parent,pos,size)
        img                 = pyglet.image.load(image_file)
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = scale
        self.image.scale    = self.scale
        self.width          = self.image.width
        self.height         = self.image.height

    def draw(self):
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = self.scale
        self.width          = self.image.width
        self.height         = self.image.height
        self.image.draw()



class MTScatterWidget(MTRectangularWidget):
    """MTScatterWidget is a scatter widget based on MTRectangularWidget"""
    def __init__(self, parent=None, pos=(0,0), size=(100,100), **kargs):
        MTRectangularWidget.__init__(self,parent, pos, size, **kargs)
        self.touches = []
        self.rotation = 0.0
        self.zoom  = 1.0

    def draw(self):
        MTRectangularWidget.draw(self)

    def on_draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotated(self.rotation, 0,0,1)
        glScalef(self.zoom, self.zoom, 1)
        glTranslatef(-self.x, -self.y, 0)
        glTranslatef(-self.width/2, -self.height/2, 0)
        glColor3d(1,0,0)
        self.draw()
        glPopMatrix()

    def collidePoint(self, x,y):
        radius = sqrt(self.width*self.width + self.height*self.height)/2 *self.zoom
        dist = Vector.length(Vector(self.x,self.y) - Vector(x,y))
        if radius >= dist:
            return True
        else:
            return False




    def updateTouchPos(self, touchID, x,y):
        #update touchPos        
        for i in range(len(self.touches)):
            if touchID == self.touches[i]["id"]:
                self.touches[i]["pos"] = Vector(x,y)

    def haveTouch(self, touchID):
        for i in range(len(self.touches)):
            if touchID == self.touches[i]["id"]:
                return True
        return False

    def save_status(self):
        for i in range(len(self.touches)):
            self.touches[i]["start_pos"] = self.touches[i]["pos"]

    def on_touch_down(self, touches, touchID, x,y):
        if not self.collidePoint(x,y):
            return
        self.bring_to_front()
        if not self.haveTouch(touchID):
            self.touches.append( {"id":touchID, "start_pos":Vector(x,y), "pos":Vector(x,y)} )
        
         

    def on_touch_move(self, touches, touchID, x,y):
        if not self.haveTouch(touchID):
            return

        self.updateTouchPos(touchID, x,y)
        if len(self.touches) == 1 :
            p1_start = self.touches[0]["start_pos"]
            p1_now   = self.touches[0]["pos"]
            translation = p1_now - p1_start
            self.x += translation.x
            self.y += translation.y

        if len(self.touches) > 1 :  #only if we have at least 2 touches do we rotate/scale
            p1_start = self.touches[0]["start_pos"]
            p2_start = self.touches[1]["start_pos"]
            p1_now   = self.touches[0]["pos"]
            p2_now   = self.touches[1]["pos"]
            
            #compute zoom
            old_dist = Vector.distance(p1_start, p2_start)
            new_dist = Vector.distance(p1_now, p2_now)
            self.zoom =  new_dist/old_dist * self.zoom

            #compute pos
            old_center = p1_start + (p2_start - p1_start)*0.5
            new_center = p1_now + (p2_now - p1_now)*0.5
            translation =  new_center - old_center
            self.x += translation.x
            self.y += translation.y

            #compute rotation
            old_line = p1_start - p2_start
            new_line = p1_now - p2_now
            self.rotation -= Vector.angle(old_line, new_line)
            
        self.save_status()

    def on_touch_up(self, touches, touchID, x,y):
        #find the touch in our record and remove it, also remove the ones that arent alive anymore...otherwise this causes a rare bug, where a touch is remembered although its dead
        #print len(self.touches), touches.keys()
        delete_indexes = [] #removing them from teh list while iterating it is a bad idea :P
        for i in range(len(self.touches)):
            if (touchID == self.touches[i]["id"]) or (self.touches[i]["id"] not in touches):
                delete_indexes.append(i)
        for index in delete_indexes:
            del self.touches[index]






class MTScatterImage(MTScatterWidget):
    """MTZoomableWidget is a zoomable Image widget"""
    def __init__(self, img_src,parent=None, pos=(0,0), size=(100,100)):
        MTScatterWidget.__init__(self,parent, pos, size)
        img         = pyglet.image.load(img_src)
        self.image  = pyglet.sprite.Sprite(img)

    def draw(self):
        glPushMatrix()        
        glTranslated(self.x, self.y, 0)
        glScaled(float(self.width)/self.image.width, float(self.height)/self.image.height, 2.0)        
        self.image.draw()
        glPopMatrix()
        #MTScatterWidget.draw(self)



class MTSlider(MTRectangularWidget):
    """MTSlider is an implementation of a scrollbar using MTRectangularWidget"""
    def __init__(self, parent=None, min=0, max=100, pos=(10,10), size=(30,400), alignment='horizontal', padding=8, color=(0.8, 0.8, 0.4, 1.0)):
        MTRectangularWidget.__init__(self, parent, pos, size)
        self.touchstarts = [] # only react to touch input that originated on this widget 
        self.alignment = alignment
        self.color = color
        self.padding = padding
        self.min, self.max = min, max
        self.value = self.min
        self.value = 77

    def draw(self):
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        x,y,w,h = self.x,self.y,self.width, self.height
        p2 =self.padding/2
        # draw outer rectangle
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner rectangle
        glColor4f(*self.color)
        length = int(self.height*(float(self.value)/self.max) - self.padding)
        drawRectangle(pos=(self.x+p2,self.y+p2), size=(w-self.padding, length) )

    def on_touch_down(self, touches, touchID, x, y):
        if self.collidePoint(x,y):
            self.touchstarts.append(touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.collidePoint(x,y) and (touchID in self.touchstarts):
            self.value = (y-self.y)/ float(self.height) *self.max
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)


class MTColorPicker(MTRectangularWidget):
    """MTColorPicker is a implementation of a color picker using MTRectangularWidget"""
    def __init__(self, parent=None, min=0, max=100, pos=(0,0), size=(640,480),target=[]):
        MTRectangularWidget.__init__(self,parent, pos, size)
        self.canvas = target[0]
        self.sliders = [ MTSlider(max=255, size=(30,200), color=(1,0,0,1)),
                        MTSlider(max=255, size=(30,200), color=(0,1,0,1)),
                        MTSlider(max=255, size=(30,200), color=(0,0,1,1)) ]
        self.update_color()
        self.touch_positions = {}

    def draw(self):
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(self.x, self.y), size=(self.width,self.height))

        glColor4f(*self.current_color)
        drawRectangle(pos=(self.x+10, self.y+220), size=(110,60))

        for i in range(len(self.sliders)):
            self.sliders[i].x = 10 + self.x + i*40
            self.sliders[i].y = 10 + self.y
            self.sliders[i].draw()

    def update_color(self):
        r = self.sliders[0].value/255.0
        g = self.sliders[1].value/255.0
        b = self.sliders[2].value/255.0
        if self.canvas:
            self.canvas.color = (r,g,b,1)
        self.current_color = (r,g,b,1.0)

    def on_touch_down(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_down(touches, touchID, x, y):
                self.update_color()
                return True

        if self.collidePoint(x,y):
            self.touch_positions[touchID] = (x,y,touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_move(touches, touchID, x, y):
                self.update_color()
                return True

        if self.touch_positions.has_key(touchID):
            self.x += x - self.touch_positions[touchID][0]
            self.y += y - self.touch_positions[touchID][1]
            self.touch_positions[touchID] = (x,y,touchID)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_up(touches, touchID, x, y):
                self.update_color()
                return True
        if self.touch_positions.has_key(touchID):
            del self.touch_positions[touchID]


class MTObjectWidget(MTRectangularWidget):
    """MTObjectWidget is a widget who draw an object on table"""
    def __init__(self, parent=None, pos=(0, 0), size=(100, 100)):
        MTRectangularWidget.__init__(self,parent, pos, size)

        self.state      = ('normal', None)
        self.visible    = False
        self.angle      = 0
        self.id         = 0

    def on_object_down(self, touches, touchID,id, x, y,angle):
        self.x ,self.y  = x, y
        self.angle      = angle/pi*180
        self.visible    = True
        self.id         = id
        self.state      = ('dragging', touchID, x, y)
        return True

    def on_object_move(self, touches, touchID, id, x, y, angle):
        if self.state[0] == 'dragging' and self.state[1] == touchID:
            self.angle      = -angle/pi*180
            self.x, self.y  = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
            self.id         = id
            self.state      = ('dragging', touchID, x, y)
            return True

    def on_object_up(self, touches, touchID,id, x, y,angle):
        if self.state[1] == touchID:
            self.angle      = -angle/pi*180
            self.visible    = False
            self.id         = id
            self.state      = ('normal', None)
            return True

    def draw(self):
        if not self.visible:
            return
        glPushMatrix()
        glTranslatef(self.x,self.y,0.0)
        glRotatef(self.angle,0.0,0.0,1.0)
        glColor3f(1.0,1.0,1.0)
        drawRectangle((-0.5*self.width, -0.5*self.height) ,(self.width, self.height))
        glColor3f(0.0,0.0,1.0)
        glBegin(GL_LINES)
        glVertex2f(0.0,0.0)
        glVertex2f(0,-0.5*self.height)
        glEnd()
        glPopMatrix()


class MTSimulator(MTWidget):
    """MTSimulator is a widget who generate touch event from mouse event"""
    def __init__(self, output, parent=None):
        MTWidget.__init__(self, parent)
        self.touches = {}
        self.pos=(100,100)
        self.output = output
        self.counter = 0
        self.current_drag = None

    def draw(self):
        for t in self.touches.values():
            p = (t.xpos,t.ypos)
            glColor4f(0.8,0.2,0.2,0.7)
            drawCircle(pos=p, radius=10)

    def find_touch(self,x,y):
        for t in self.touches.values():
            if (abs(x-t.xpos) < 10 and abs(y-t.ypos) < 10):
                return t
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        newTouch = self.find_touch(x,y)
        if newTouch:
            self.current_drag = newTouch
        else: #new touch is added 
            self.counter += 1
            id = 'mouse'+str(self.counter)
            self.current_drag = cursor = Tuio2DCursor(id, [x,y])
            self.touches[id] = cursor
            self.output.dispatch_event('on_touch_down', self.touches, id, x, y)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        cur = self.current_drag
        cur.xpos, cur.ypos = x,y
        self.output.dispatch_event('on_touch_move', self.touches, cur.blobID, x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        t = self.find_touch(x,y)
        if  button == 1 and t and not(modifiers & key.MOD_CTRL):
            self.output.dispatch_event('on_touch_up', self.touches, self.current_drag.blobID, x, y)
            del self.touches[self.current_drag.blobID]

class XMLWidget(MTWidget):
    def __init__(self, parent=None, xml=None):
        MTWidget.__init__(self, parent)
        if xml is not None:
            self.loadString(xml)

    def createNode(self, node):
        if node.nodeType == Node.ELEMENT_NODE:
            class_name = node.nodeName

            #create widget
            nodeWidget  = MTWidgetFactory.get(class_name)( parent=None )

            #set attributes
            for (name, value) in node.attributes.items():
                nodeWidget.__setattr__(name, eval(value))

            #add child widgets
            for c in node.childNodes:
                w = self.createNode(c)
                if w:
                    nodeWidget.add_widget(w)

            return nodeWidget

    def loadString(self, xml):
        doc = minidom.parseString(xml)
        root = doc.documentElement
        self.add_widget(self.createNode(root))


def showNode(node):
	if node.nodeType == Node.ELEMENT_NODE:
		print 'Element name: %s' % node.nodeName
		for (name, value) in node.attributes.items():
			print '    Attr -- Name: %s  Value: %s' % (name, value)
		if node.attributes.get('ID') is not None:
			print '    ID: %s' % node.attributes.get('ID').value



"""TODO: Layouts...not used anywhere yet"""
class HorizontalLayout(MTRectangularWidget):
	def __init__(self, parent=None, spacing=10, **kargs):
		MTRectangularWidget.__init__(self, parent, **kargs)
		self.spacing = spacing
		
	def draw(self):
		MTWidget.draw(self)
		
	def add_widget(self,w):
		MTWidget.add_widget(self, w)
		self.layout()
		
	def layout(self):
		cur_x = self.x
		for w in self.children:
			try:
				w.x = cur_x
				cur_x += w.width + spacing
			except:
				pass





# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
MTWidgetFactory.register('MTWindow', MTWindow)
MTWidgetFactory.register('MTDisplay', MTDisplay)
MTWidgetFactory.register('MTContainer', MTContainer)
MTWidgetFactory.register('MTRectangularWidget', MTRectangularWidget)
MTWidgetFactory.register('MTDragableWidget', MTDragableWidget)
MTWidgetFactory.register('MTButton', MTButton)
MTWidgetFactory.register('MTImageButton', MTImageButton)
MTWidgetFactory.register('MTScatterWidget', MTScatterWidget)
#MTWidgetFactory.register('MTZoomableWidget', MTZoomableWidget)
MTWidgetFactory.register('MTScatterImage', MTScatterImage)
MTWidgetFactory.register('MTSlider', MTSlider)
MTWidgetFactory.register('MTColorPicker', MTColorPicker)
MTWidgetFactory.register('MTObjectWidget', MTObjectWidget)
MTWidgetFactory.register('MTSimulator', MTSimulator)
MTWidgetFactory.register('XMLWidget', XMLWidget)

