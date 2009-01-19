from pyglet import *
from pyglet.gl import *
from pymt.graphx import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widget import MTWidget
from pymt.ui.simulator import MTSimulator
from pymt.vector import Vector

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
                    return True

    def on_touch_move(self, touches, touchID, x, y):
        for l in self.layers:
            for w in reversed(l):
                if w.dispatch_event('on_touch_move', touches, touchID, x, y):
                    return True

    def on_touch_up(self, touches, touchID, x, y):
        for l in self.layers:
            for w in reversed(l):
                if w.dispatch_event('on_touch_up', touches, touchID, x, y):
                    return True

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

    def get_size(self):
        return (self.width, self.height)

    def draw(self):
        glColor4d(*self.color)
        drawRectangle((self.x, self.y), (self.width, self.height))

    def consumes_event(self, x,y):
        return self.collide_point(x,y)

    def to_local(self,x,y):
        lx = (x - self.x)
        ly = (y - self.y)
        return (lx,ly)

    def collide_point(self, x, y):
        if( x > self.x  and x < self.x + self.width and
           y > self.y and y < self.y + self.height  ):
            return True

    def on_resize(self, w, h):
        for c in self.children:
            c.dispatch_event('on_resize', w, h)

    def on_move(self, x, y):
        for c in self.children:
            c.dispatch_event('on_move', x, y)

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
        if self.collide_point(x,y):
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
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[1] == touchID and not self.collide_point(x,y):
            self.state = ('normal', 0)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID and self.collide_point(x,y):
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
        self.testPos = Vector(0,0)

    def draw(self):
        glColor4d(1,0,1,0)
        drawRectangle((0,0), (self.width, self.height))


    def on_draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glTranslatef(self.width/2, self.height/2, 0)
        glScalef(self.zoom, self.zoom, 1)
        glRotated(self.rotation, 0,0,1)
        glTranslatef(-self.width/2, -self.height/2, 0)
        glColor3d(1,0,0)
        self.draw()
        glPopMatrix()

    def _set_width(self, w):
        self._width = w
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_width(self):
        return self._width*self.zoom


    def _set_height(self, h):
        self._height = h
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_height(self):
        return self._height*self.zoom


    def _set_size(self, size):
        self.width, self.height = size
        self.dispatch_event('on_resize', self.width, self.height)
    def _get_size(self):
        return (int(self.width*self.zoom), int(self.height*self.zoom))


    def collide_point(self, x,y):
        local_coords = self.to_local(x,y)
        if local_coords[0] > 0 and local_coords[0] < self.width \
           and local_coords[1] > 0 and local_coords[1] < self.height:
            return True
        else:
            return False

    def updateTouchPos(self, touchID, x,y):
        for i in range(len(self.touches)):
            if touchID == self.touches[i]["id"]:
                self.touches[i]["pos"] = Vector(x,y)

    def haveTouch(self, touchID):
        for i in range(len(self.touches)):
            if touchID == self.touches[i]["id"]:
                return True
        return False

    def to_local(self,x,y):
        #local center x,y ..around which we rotate 
        lcx = (x - self.x ) - self.width/2
        lcy = (y - self.y ) - self.height/2        
      
        #rotate around the center(its moved center to 0,0) then move back to position
        angle = radians(-self.rotation)
        lx= ( lcx*cos(angle)-lcy*sin(angle) ) *1.0/self.zoom
        ly= ( lcx*sin(angle)+lcy*cos(angle) ) *1.0/self.zoom
        return (lx+ self.width/2,ly+ self.height/2)

    def save_status(self):
        for i in range(len(self.touches)):
            self.touches[i]["start_pos"] = self.touches[i]["pos"]

    def on_touch_down(self, touches, touchID, x,y):
        if not self.collide_point(x,y):
            return False
        self.bring_to_front()
        if not self.haveTouch(touchID):
            self.touches.append( {"id":touchID, "start_pos":Vector(x,y), "pos":Vector(x,y)} )
        return True

    def on_touch_move(self, touches, touchID, x,y):
        self.testPos.x, self.testPos.y = self.to_local(x,y)

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
        return True

    def on_touch_up(self, touches, touchID, x,y):
        #find the touch in our record and remove it, also remove the ones that arent alive anymore...otherwise this causes a rare bug, where a touch is remembered although its dead
        #print len(self.touches), touches.keys()
        delete_indexes = [] #removing them from teh list while iterating it is a bad idea :P
        for i in range(len(self.touches)):
            if (touchID == self.touches[i]["id"]) or (self.touches[i]["id"] not in touches):
                delete_indexes.append(i)
        for index in delete_indexes:
            del self.touches[index]
        if self.collide_point(x,y):
            return True



class MTScatterImage(MTScatterWidget):
    """MTZoomableWidget is a zoomable Image widget"""
    def __init__(self, img_src,parent=None, pos=(0,0), size=(100,100)):
        MTScatterWidget.__init__(self,parent, pos, size)
        img         = pyglet.image.load(img_src)
        self.image  = pyglet.sprite.Sprite(img)

    def draw(self):
        glPushMatrix()
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
        if self.collide_point(x,y):
            self.touchstarts.append(touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.collide_point(x,y) and (touchID in self.touchstarts):
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

        if self.collide_point(x,y):
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

# Register all base widgets
MTWidgetFactory.register('MTContainer', MTContainer)
MTWidgetFactory.register('MTRectangularWidget', MTRectangularWidget)
MTWidgetFactory.register('MTDragableWidget', MTDragableWidget)
MTWidgetFactory.register('MTButton', MTButton)
MTWidgetFactory.register('MTImageButton', MTImageButton)
MTWidgetFactory.register('MTScatterWidget', MTScatterWidget)
MTWidgetFactory.register('MTScatterImage', MTScatterImage)
MTWidgetFactory.register('MTSlider', MTSlider)
MTWidgetFactory.register('MTColorPicker', MTColorPicker)
MTWidgetFactory.register('MTObjectWidget', MTObjectWidget)

