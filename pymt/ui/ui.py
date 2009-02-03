from pyglet import *
from pyglet.gl import *
from pymt.graphx import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widget import MTWidget
from pymt.ui.simulator import MTSimulator
from pymt.ui.layout import HVLayout
from pymt.vector import *


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
    def __init__(self, **kwargs):
        super(MTDragableWidget, self).__init__(**kwargs)
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
    '''MTButton is a button implementation using MTWidget

    :Parameters:
        `label` : string, default is ''
            Label of button
        `color_down` : list, default is (.5, .5, .5, .5)
            Color of button when pushed
        `anchor_x`: string
            X anchor of label, refer to pyglet.label.anchor_x documentation
        `anchor_y`: string
            Y anchor of label, refer to pyglet.label.anchor_x documentation
        `font_size`: integer, default is 10
            Font size of label
        `bold`: bool, default is True
            Font bold of label
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('anchor_x', 'center')
        kwargs.setdefault('anchor_y', 'center')
        kwargs.setdefault('font_size', 10)
        kwargs.setdefault('bold', True)
        kwargs.setdefault('color_down', (.5, .5, .5, .5))

        super(MTButton, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')

        self._state         = ('normal', 0)
        self.clickActions   = []
        self.label_obj      = Label(font_size=kwargs.get('font_size'), bold=kwargs.get('bold'))
        self.label_obj.anchor_x = kwargs.get('anchor_x')
        self.label_obj.anchor_y = kwargs.get('anchor_y')
        self.label_obj.text = str(kwargs.get('label'))
        self._label         = str(kwargs.get('label'))
        self.color_down     = kwargs.get('color_down')

    def get_label(self):
        return self._label
    def set_label(self, text):
        self._label = str(text)
        self.label_obj.text = self._label
    label = property(get_label, set_label)

    def get_state(self):
        return self._state[0]
    def set_state(self, state):
        self._state = (state, 0)
    state = property(get_state, set_state, doc='Sets the state of the button, "normal" or "down"')

    def draw(self):
        # Select color
        if self._state[0] == 'down':
            glColor4f(*self.color_down)
        else:
            glColor4f(*self.color)

        # Try to optimize, use display if possible
        drawRectangle(self.pos, self.size)

        if len(self._label):
            self.label_obj.x, self.label_obj.y = self.x +self.width/2 , self.y + +self.height/2
            self.label_obj.draw()

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self._state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x,y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self._state[1] == touchID and not self.collide_point(x,y):
            self._state = ('normal', 0)
            return True
        return self.collide_point(x,y)

    def on_touch_up(self, touches, touchID, x, y):
        if self._state[1] == touchID and self.collide_point(x,y):
            self._state = ('normal', 0)
            self.dispatch_event('on_release', touchID, x,y)
            return True
        return self.collide_point(x,y)


class MTToggleButton(MTButton):
    '''Toggle button implementation, based on MTButton'''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', 'ToggleButton')
        super(MTToggleButton, self).__init__(**kwargs)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            if self.get_state() == 'down':
                self._state = ('normal', touchID)
            else:
                self._state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x,y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self._state[1] == touchID and not self.collide_point(x,y):
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self._state[1] == touchID and self.collide_point(x,y):
            self.dispatch_event('on_release', touchID, x,y)
            return True


class MTImageButton(MTButton):
    '''MTImageButton is a enhanced MTButton
    that draw an image instead of a text.

    :Parameters:
        `filename` : str
            Filename of image
        `scale` : float, default is 1.0
            Scaling of image, default is 100%, ie 1.0
    '''
    def __init__(self, **kwargs):
        # Preserve this way to do
        # Later, we'll give another possibility, like using a loader...
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTImageButton')

        super(MTImageButton, self).__init__(**kwargs)
        img                 = pyglet.image.load(kwargs.get('filename'))
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
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


class MTButtonMatrix(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('matrix_size', (3,3))
        kwargs.setdefault('spacing', 1)
        super(MTButtonMatrix, self).__init__(**kwargs)
        self.matrix_size = kwargs.get('matrix_size')
        self.spacing = kwargs.get('spacing')
        self.buttons = []

        vlayout = HVLayout(alignment = 'vertical', spacing = self.spacing)
        for l in range(self.matrix_size[1]):
            hlayout = HVLayout(spacing = self.spacing)
            for btn in range(self.matrix_size[0]):
                b = MTToggleButton(size = (20,20), label = '')
                hlayout.add_widget(b)
                self.buttons.append(b)
            vlayout.add_widget(hlayout)
        self.add_widget(vlayout)


class MTScatterWidget(MTWidget):
    '''MTScatterWidget is a scatter widget based on MTWidget

    :Parameters:
        `draw_children` : bool, default is True
            Indicate if children will be draw, or not
        `rotation` : float, default to 0
            Set rotation of widget
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('draw_children', True)
        kwargs.setdefault('rotation', 0)

        super(MTScatterWidget, self).__init__(**kwargs)
        self.touches = {}
        self.transform_mat = (GLfloat * 16)()
        self.draw_children = kwargs.get('draw_children')
        self.init_transform(self.pos, kwargs.get('rotation'))


    def init_transform(self, pos, angle):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslated(pos[0], pos[1], 0)
        glRotated(angle,0,0,1)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.transform_mat)
        glPopMatrix()

    def draw(self):
        glColor4d(*self.color)
        drawRectangle((0,0), (self.width, self.height))

    def on_draw(self):
        glPushMatrix()
        glMultMatrixf(self.transform_mat)
        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')
        glPopMatrix()

    def to_local(self,x,y):
        self.new_point = matrix_inv_mult(self.transform_mat, (x,y,0,1))
        return (self.new_point.x, self.new_point.y)

    def collide_point(self, x,y):
        local_coords = self.to_local(x,y)
        if local_coords[0] > 0 and local_coords[0] < self.width \
           and local_coords[1] > 0 and local_coords[1] < self.height:
            return True
        else:
            return False

    def find_second_touch(self, touchID):
        for tID in self.touches.keys():
            x,y = self.touches[tID].x, self.touches[tID].y
            if self.collide_point(x,y) and tID!=touchID:
                return tID
        return None

    def rotate_zoom_move(self, touchID, x, y):
        # some default values, in case we dont calculate them,
        # they still need to be defined for applying the openGL transformations
        intersect = Vector(0,0)
        trans = Vector(0,0)
        rotation = 0
        scale = 1

        # we definitly have one point
        p1_start = self.touches[touchID]
        p1_now   = Vector(x,y)

        # if we have a second point, do the scale/rotate/move thing
        second_touch = self.find_second_touch(touchID)
        if second_touch:
            p2_start = self.touches[second_touch]
            p2_now   = self.touches[second_touch]

            # find intersection between lines...the point around which to rotate
            intersect = Vector.line_intersection(p1_start,  p2_start,p1_now, p2_now)
            if not intersect:
                intersect = Vector(0,0)

            # compute scale factor
            old_dist = Vector.distance(p1_start, p2_start)
            new_dist = Vector.distance(p1_now, p2_now)
            scale = new_dist/old_dist

            # compute rotation angle
            old_line = p1_start - p2_start
            new_line = p1_now - p2_now
            rotation = -Vector.angle(old_line, new_line)

        else:
            # just comnpute a translation component if we only have one point
            trans = p1_now - p1_start

        # apply to our transformation matrix
        glPushMatrix()
        glLoadIdentity()
        glTranslated(trans.x, trans.y,0)
        glTranslated(intersect.x, intersect.y,0)
        glScaled(scale, scale,1)
        glRotated(rotation,0,0,1)
        glTranslated(-intersect.x, -intersect.y,0)
        glMultMatrixf(self.transform_mat)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.transform_mat)
        glPopMatrix()

        
        # save new position of the current touch
        self.touches[touchID] = Vector(x,y)

    def get_scale_factor(self):
        p1_trans = matrix_mult(self.transform_mat, (1,1,0,1))
        p2_trans = matrix_mult(self.transform_mat, (2,1,0,1))
        dist_trans = Vector.distance(p1_trans, p2_trans)
        return dist_trans

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
        self.touches[touchID] = Vector(x,y)
        return True

    def on_touch_move(self, touches, touchID, x,y):
        # if the touch isnt on teh widget we do nothing
        if not (self.collide_point(x,y) or touchID in self.touches):
            return False

        #rotate/scale/translate
        if touchID in self.touches:
            self.rotate_zoom_move(touchID, x, y)
            self.dispatch_event('on_resize', int(self.width*self.get_scale_factor()), int(self.height*self.get_scale_factor()))
            self.dispatch_event('on_move', self.x, self.y)
            return True

        #let the child widgets handle the event if they want an we did not
        lx,ly = self.to_local(x,y)
        if MTWidget.on_touch_move(self, touches, touchID, lx, ly):
            return True

        #stop porpagation if its within our bounds
        if self.collide_point(x,y):
            return True

    def on_touch_up(self, touches, touchID, x,y):
        #if the touch isnt on the widget we do nothing
        lx,ly = self.to_local(x,y)
        MTWidget.on_touch_up(self, touches, touchID, lx, ly)

        #remove it from our saved touches
        if self.touches.has_key(touchID):
            del self.touches[touchID]

        #stop porpagating if its within our bounds
        if  self.collide_point(x,y):
            return True


class MTScatterImage(MTScatterWidget):
    '''MTScatterImage is a image showed in a Scatter widget

    :Parameters:
        `filename` : str
            Filename of image
        `loader` : Loader instance
            Use the loader to load image
    '''
    def __init__(self, **kwargs):
        # Preserve this way to do
        # Later, we'll give another possibility, like using a loader...
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTScatterImage')
        kwargs.setdefault('loader', None)

        super(MTScatterImage, self).__init__(**kwargs)

        # Use loader if available
        loader = kwargs.get('loader')
        if loader:
            self.image  = loader.sprite(kwargs.get('filename'))
        else:
            img         = pyglet.image.load(kwargs.get('filename'))
            self.image  = pyglet.sprite.Sprite(img)

    def draw(self):
        glPushMatrix()
        glScaled(float(self.width)/self.image.width, float(self.height)/self.image.height, 2.0)
        self.image.draw()
        glPopMatrix()


class MTSlider(MTWidget):
    '''MTSlider is an implementation of a scrollbar using MTWidget.

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 100
            Maximum value of slider
        `orientation` : str, default is vertical
            Type of orientation, can be 'horizontal' or 'vertical'
        `value` : int, default is `min`
            Default value of slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 100)
        kwargs.setdefault('padding', 8)
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('color', (.8, .8, .4, 1.0))
        kwargs.setdefault('size', (30, 400))
        kwargs.setdefault('value', None)

        super(MTSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts    = [] # only react to touch input that originated on this widget
        self.orientation      = kwargs.get('orientation')
        self.padding        = kwargs.get('padding')
        self.min            = kwargs.get('min')
        self.max            = kwargs.get('max')
        self._value         = self.min
        if kwargs.get('value'):
            self._value = kwargs.get('value')

    def on_value_change(self, value):
        pass

    def set_value(self, _value):
        self._value = _value
        self.dispatch_event('on_value_change', self._value)
    def get_value(self):
        return self._value
    value = property(get_value, set_value, doc='Value of the slider')

    def draw(self):
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        x,y,w,h = self.x, self.y, self.width, self.height
        p2 =self.padding/2
        # draw outer rectangle
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner rectangle
        glColor4f(*self.color)
        if self.orientation == 'vertical':
            length = int((self._value - self.min) * (self.height - self.padding) / (self.max - self.min))
            drawRectangle(pos=(x+p2,y+p2), size=(w - self.padding, length))
        else:
            length = int((self._value - self.min) * (self.width - self.padding) / (self.max - self.min))
            drawRectangle(pos=(x+p2,y+p2), size=(length, h - self.padding))

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.touchstarts.append(touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            last_value = self._value
            if self.orientation == 'vertical':
                self._value = (y - self.y) * (self.max - self.min) / float(self.height) + self.min
            else:
                self._value = (x - self.x) * (self.max - self.min) / float(self.width) + self.min
            if self._value >= self.max:
                self._value = self.max
            if self._value <= self.min:
                self._value = self.min
            if not self._value == last_value:
                self.dispatch_event('on_value_change', self._value)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)

class MT2DSlider(MTWidget):
    '''MT2DSlider is an implementation of a 2D slider using MTWidget.

    :Parameters:
        `min_x` : int, default is 20
            Minimum value of slider
        `max_x` : int, default is 100
            Maximum value of slider
        `min_y` : int, default is 20
            Minimum value of slider
        `max_y` : int, default is 100
            Maximum value of slider
        `radius` : int, default is 200
            Radius of the slider handle
        `value_x` : int, default is `min_x`
            Default X value of slider
        `value_y` : int, default is `min_y`
            Default Y value of slider
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min_x', 20)
        kwargs.setdefault('max_x', 100)
        kwargs.setdefault('min_y', 20)
        kwargs.setdefault('max_y', 100)
        kwargs.setdefault('radius', 20)
        kwargs.setdefault('size', (200, 200))
        kwargs.setdefault('value_x', None)
        kwargs.setdefault('value_y', None)
        kwargs.setdefault('color', (.8, .8, .4, 1.0))

        super(MT2DSlider, self).__init__(**kwargs)
        self.register_event_type('on_value_change')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.radius     = kwargs.get('radius')
        self.padding    = kwargs.get('radius')
        self.min_x      = kwargs.get('min_x')
        self.max_x      = kwargs.get('max_x')
        self.min_y      = kwargs.get('min_y')
        self.max_y      = kwargs.get('max_y')
        self.radius     = kwargs.get('radius')
        self._value_x, self._value_y = self.min_x, self.min_y
        if kwargs.get('value_x'):
            self._value_x = kwargs.get('value_x')
        if kwargs.get('value_y'):
            self._value_y = kwargs.get('value_y')

    def on_value_change(self, value_x, value_y):
        pass

    def set_value_x(self, value):
        self._value_x = value
        self.dispatch_event('on_value_change', self._value_x, self._value_y)
        self.draw()

    def get_value_x(self):
        return self._value_x

    value_x = property(get_value_x, set_value_x, doc='Value of the slider (x axis)')

    def set_value_y(self, value):
        self._value_y = value
        self.dispatch_event('on_value_change', self._value_x, self._value_y)
        self.draw()

    def get_value_y(self):
        return self._value_y

    value_y = property(get_value_y, set_value_y, doc='Value of the slider (y axis)')

    def draw(self):
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        x,y,w,h = self.x,self.y,self.width, self.height
        # draw outer rectangle
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner circle
        glColor4f(*self.color)
        pos_x = int((self._value_x - self.min_x) * (self.width - self.padding*2) / (self.max_x - self.min_x))  + self.x + self.padding
        pos_y = int((self._value_y - self.min_y) * (self.height - self.padding*2) / (self.max_y - self.min_y)) + self.y + self.padding
        drawCircle(pos=(pos_x, pos_y), radius = self.radius)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.touchstarts.append(touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            last_value_x, last_value_y = self._value_x, self._value_y
            self._value_x = (x - self.x) * (self.max_x - self.min_x) / float(self.width) + self.min_x
            self._value_y = (y - self.y) * (self.max_y - self.min_y) / float(self.height) + self.min_y
            if self._value_x >= self.max_x:
                self._value_x = self.max_x
            if self._value_x <= self.min_x:
                self._value_x = self.min_x
            if self._value_y >= self.max_y:
                self._value_y = self.max_y
            if self._value_y <= self.min_y:
                self._value_y = self.min_y
            if not self._value_x == last_value_x or not self._value_y == last_value_y:
                self.dispatch_event('on_value_change', self._value_x, self._value_y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)


class MTColorPicker(MTWidget):
    '''MTColorPicker is a implementation of a color picker using MTWidget

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 255
            Maximum value of slider
        `targets` : list, default is []
            List of widget to be affected by change
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 255)
        kwargs.setdefault('target', [])
        super(MTColorPicker, self).__init__(**kwargs)
        self.targets = targets
        self.sliders = [ MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), color=(1,0,0,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), color=(0,1,0,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), color=(0,0,1,1)) ]
        for slider in self.sliders:
            slider.value = 77
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
        for w in self.targets:
            w.color = (r,g,b,1)
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
    def __init__(self, **kwargs):
        super(MTObjectWidget, self).__init__(**kwargs)
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
MTWidgetFactory.register('MTMatrixButton', MTImageButton)
MTWidgetFactory.register('MTScatterWidget', MTScatterWidget)
MTWidgetFactory.register('MTScatterImage', MTScatterImage)
MTWidgetFactory.register('MTSlider', MTSlider)
MTWidgetFactory.register('MT2DSlider', MT2DSlider)
MTWidgetFactory.register('MTColorPicker', MTColorPicker)
MTWidgetFactory.register('MTObjectWidget', MTObjectWidget)
