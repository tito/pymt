from pyglet import *
from pyglet.gl import *
from pymt.graphx import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widget import MTWidget
from pymt.ui.simulator import MTSimulator
from pymt.vector import Vector


class MTRectangularWidget(MTWidget):
    '''A rectangular widget that only propagates and handles events if the event was within its bounds'''
    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            super(MTRectangularWidget, self).on_touch_down(touches, touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            super(MTRectangularWidget, self).on_touch_move(touches, touchID, x, y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            super(MTRectangularWidget, self).on_touch_up(touches, touchID, x, y)
            return True

    def draw(self):
        set_color(*self.color)
        drawRectangle(self.pos, self.size)


class MTDragableWidget(MTWidget):
    '''MTDragableWidget is a moveable widget over the window'''
    def __init__(self, pos=(0,0), size=(100,100), **kargs):
        super(MTDragableWidget, self).__init__(pos=pos, size=size, **kargs)
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


class MTButton(MTWidget):
    '''MTButton is a button implementation using MTWidget'''
    def __init__(self, pos=(0, 0), size=(100, 100), label='', color=(0.2,0.2,0.2,0.8),**kargs):
        super(MTButton, self).__init__(pos=pos, size=size, color=color, **kargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        self.state          = ('normal', 0)
        self.clickActions   = []
        self.label_obj      = Label(font_size=10, bold=True )
        self.label_obj.anchor_x = 'center'
        self.label_obj.anchor_y = 'center'
        self._label          = str(label)

    def get_label(self):
        return self._label
    def set_label(self, text):
        self._label = str(text)
        #self.label_obj.text = self._label
    label = property(get_label, set_label)

    def get_state(self):
        return self.state[0]

    def set_state(self, state):
        self.state = (state, 0)
        self.draw()

    def draw(self):
        if self.state[0] == 'down':
            glColor4f(0.5,0.5,0.5,0.5)
            drawRectangle((self.x,self.y) , (self.width, self.height))
        else:
            glColor4f(*self.color)
            drawRectangle((self.x,self.y) , (self.width, self.height))

        #self.label_obj.x, self.label_obj.y = self.x +self.width/2 , self.y + +self.height/2
        #self.label_obj.draw()
        #print "drawing label", self.label
        drawLabel(self.label, self.center)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x,y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[1] == touchID and not self.collide_point(x,y):
            self.state = ('normal', 0)
            return True
        return self.collide_point(x,y)

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID and self.collide_point(x,y):
            self.state = ('normal', 0)
            self.dispatch_event('on_release', touchID, x,y)
            return True
        return self.collide_point(x,y)


class MTToggleButton(MTButton):
    def __init__(self, pos=(0, 0), size=(100, 100), label='ToggleButton', **kargs):
        super(MTToggleButton, self).__init__(pos=pos, size=size, label=label, **kargs)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            if self.get_state() == 'down':
                self.state = ('normal', touchID)
            else:
                self.state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x,y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[1] == touchID and not self.collide_point(x,y):
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID and self.collide_point(x,y):
            self.dispatch_event('on_release', touchID, x,y)
            return True


class MTImageButton(MTButton):
    '''MTImageButton is a enhanced MTButton that draw an image instead of a text'''
    def __init__(self, image_file, pos=(0,0), size=(1,1), scale = 1.0, opacity = 100, **kargs):
        super(MTImageButton, self).__init__(pos=pos, size=size)
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


class MTScatterWidget(MTWidget):
    '''MTScatterWidget is a scatter widget based on MTWidget'''
    def __init__(self, pos=(0,0), size=(100,100), **kargs):
        super(MTScatterWidget, self).__init__(pos=pos, size=size, **kargs)
        self.touches = []
        self.rotation = 0.0
        self.zoom  = 1.0
        self.testPos = Vector(0,0)
        self.draw_children = True

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

        # propagates to children
        if self.draw_children:
            super(MTScatterWidget, self).on_draw()

        glPopMatrix()


    '''
    def _set_width(self, w):
        self._width = w
        self.dispatch_event('on_resize', self._width, self._height)
    def _get_width(self):
        return self._width*self.zoom
    width = property(_get_width, _set_width)

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
    '''

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

    def save_status(self):
        for i in range(len(self.touches)):
            self.touches[i]["start_pos"] = self.touches[i]["pos"]

    def haveTouch(self, touchID):
        for i in range(len(self.touches)):
            if touchID == self.touches[i]["id"]:
                return True
        return False

    def to_local(self,x,y):
        # local center x,y ..around which we rotate
        lcx = (x - self.x ) - self.width/2
        lcy = (y - self.y ) - self.height/2

        # rotate around the center(its moved center to 0,0) then move back to position
        angle = radians(-self.rotation)
        lx= ( lcx*cos(angle)-lcy*sin(angle) ) *1.0/self.zoom
        ly= ( lcx*sin(angle)+lcy*cos(angle) ) *1.0/self.zoom
        return (lx+ self.width/2,ly+ self.height/2)

    def rotate_zoom_move(self, touchID, x, y):
        self.updateTouchPos(touchID, x,y)
        if len(self.touches) == 1 :
            p1_start = self.touches[0]["start_pos"]
            p1_now   = self.touches[0]["pos"]
            translation = p1_now - p1_start
            self.x += translation.x
            self.y += translation.y

        if len(self.touches) > 1 :  # only if we have at least 2 touches do we rotate/scale
            p1_start = self.touches[0]["start_pos"]
            p2_start = self.touches[1]["start_pos"]
            p1_now   = self.touches[0]["pos"]
            p2_now   = self.touches[1]["pos"]

            # compute zoom
            old_dist = Vector.distance(p1_start, p2_start)
            new_dist = Vector.distance(p1_now, p2_now)
            scale = new_dist/old_dist
            self.zoom =  scale * self.zoom

            # compute pos
            old_center = p1_start + (p2_start - p1_start)*0.5
            new_center = p1_now + (p2_now - p1_now)*0.5
            translation =  new_center - old_center
            self.x += translation.x
            self.y += translation.y

            # compute rotation
            old_line = p1_start - p2_start
            new_line = p1_now - p2_now
            self.rotation -= Vector.angle(old_line, new_line)

        self.save_status()


    def on_touch_down(self, touches, touchID, x,y):
        # if the touch isnt on teh widget we do nothing
        if not self.collide_point(x,y):
            return False

        # let the child widgets handle the event if they want
        lx,ly = self.to_local(x,y)
        if super(MTScatterWidget, self).on_touch_down(touches, touchID, lx, ly):
            return True

        # if teh children didnt handle it, we bring to front & keep track of touches for rotate/scale/zoom action
        self.bring_to_front()
        if not self.haveTouch(touchID) and len(self.touches) <=2:
            self.touches.append( {"id":touchID, "start_pos":Vector(x,y), "pos":Vector(x,y)} )

        return True

    def on_touch_move(self, touches, touchID, x,y):

        #if this touch is used for rotate_scale_move,...do that
        if self.haveTouch(touchID):
            self.rotate_zoom_move(touchID, x, y)
            self.dispatch_event('on_resize', self.width, self.height)
            self.dispatch_event('on_move', self.x, self.y)
            return True

        #let the child widgets handle the event if we want
        lx,ly = self.to_local(x,y)
        if MTWidget.on_touch_move(self, touches, touchID, lx, ly):
            return True

    def on_touch_up(self, touches, touchID, x,y):
        #if the touch isnt on the widget we do nothing
        lx,ly = self.to_local(x,y)
        MTWidget.on_touch_up(self, touches, touchID, lx, ly)


        #if this touch is used for rotate_scale_move, clean up
        if self.haveTouch(touchID):
            if len(self.touches)  < 2:
                self.touches = []
                return True
            #if this was one of the two..only remove one of them
            if self.touches[0]['id'] == touchID:
                self.touches = [self.touches[1]]
            else:
                self.touches = [self.touches[0]]
            return True

        if not self.collide_point(x,y):
            return False



class MTScatterImage(MTScatterWidget):
    def __init__(self, img_src, pos=(0,0), size=(100,100)):
        super(MTScatterImage, self).__init__(pos=pos, size=size)
        img         = pyglet.image.load(img_src)
        self.image  = pyglet.sprite.Sprite(img)

    def draw(self):
        glPushMatrix()
        glScaled(float(self.width)/self.image.width, float(self.height)/self.image.height, 2.0)
        self.image.draw()
        glPopMatrix()


class MTSlider(MTWidget):
    '''MTSlider is an implementation of a scrollbar using MTWidget'''
    def __init__(self, min=0, max=100, pos=(10,10), size=(30,400), alignment='horizontal', padding=8, color=(0.8, 0.8, 0.4, 1.0)):
        super(MTSlider, self).__init__(pos=pos, size=size)
        self.register_event_type('on_value_change')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.alignment = alignment
        self.color = color
        self.padding = padding
        self.min, self.max = min, max
        self.value = self.min

    def on_value_change(self, value):
        pass

    def set_value(self, value):
        self.value = value
        self.dispatch_event('on_value_change', self.value)
        self.draw()

    def get_value():
        return self.value

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
            self.dispatch_event('on_value_change', self.value)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)


class MTColorPicker(MTWidget):
    '''MTColorPicker is a implementation of a color picker using MTWidget'''
    def __init__(self, min=0, max=100, pos=(0,0), size=(640,480),target=[]):
        super(MTColorPicker, self).__init__(pos=pos, size=size)
        self.canvas = target[0]
        self.sliders = [ MTSlider(max=255, size=(30,200), color=(1,0,0,1)),
                        MTSlider(max=255, size=(30,200), color=(0,1,0,1)),
                        MTSlider(max=255, size=(30,200), color=(0,0,1,1)) ]
        for slider in self.sliders:
            slider.set_value(77)
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


class MTObjectWidget(MTWidget):
    '''MTObjectWidget is a widget who draw an object on table'''
    def __init__(self, pos=(0, 0), size=(100, 100)):
        super(MTObjectWidget, self).__init__(pos=pos, size=size)

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
MTWidgetFactory.register('MTDragableWidget', MTDragableWidget)
MTWidgetFactory.register('MTButton', MTButton)
MTWidgetFactory.register('MTToggleButton', MTToggleButton)
MTWidgetFactory.register('MTImageButton', MTImageButton)
MTWidgetFactory.register('MTScatterWidget', MTScatterWidget)
MTWidgetFactory.register('MTScatterImage', MTScatterImage)
MTWidgetFactory.register('MTSlider', MTSlider)
MTWidgetFactory.register('MTColorPicker', MTColorPicker)
MTWidgetFactory.register('MTObjectWidget', MTObjectWidget)
