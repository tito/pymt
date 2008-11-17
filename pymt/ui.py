#!/usr/bin/env python

from pyglet import *
from pyglet.gl import *
from mtpyglet import TouchWindow
from graphx import *
from math import *




class UIWindow(TouchWindow):
	def __init__(self, view, fullscreen=False):
		config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
		TouchWindow.__init__(self, config)
		if fullscreen:
			self.set_fullscreen()
		self.active_view = view
		self.active_view.parent = self
	
	def on_draw(self):
		self.clear()
		self.active_view.draw()

	def on_touch_down(self, touches, touchID, x, y):
		#print "test", self.active_view
		self.active_view.on_touch_down(touches, touchID, x, y)
	
	def on_touch_move(self, touches, touchID, x, y):
		self.active_view.on_touch_move(touches, touchID, x, y)

	def on_touch_up(self, touches, touchID, x, y):
		self.active_view.on_touch_up(touches, touchID, x, y)
		
#------ Object --- by Felipe Carvalho

	def on_object_down(self, touches, touchID,id, x, y,angle):
		self.active_view.on_object_down(touches, touchID,id, x, y,angle)
	
	def on_object_move(self, touches, touchID,id, x, y,angle):
		self.active_view.on_object_move(touches, touchID,id, x, y,angle)

	def on_object_up(self, touches, touchID,id, x, y,angle):
		self.active_view.on_object_up(touches, touchID,id, x, y,angle)				

class Animation(object):
	def __init__(self, widget, label, prop, to, timestep, length):
		self.widget = widget
		self.frame = 0.0
		self.prop = prop
		self.to = to
                self.fro = self.widget.__dict__[self.prop]
		self.timestep = timestep
		self.length = length
		self.label = label
		
	def get_current_value(self):
		return  (1.0-self.frame/self.length) * self.fro  +  self.frame/self.length * self.to 
		
	def start(self):
		#print 'calling'
		self.reset()
		pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
		
	def reset(self):
                self.fro = self.widget.__dict__[self.prop]
		self.frame = 0.0
		
	def advance_frame(self, dt):
		self.frame += self.timestep
		self.widget.__dict__[self.prop] = self.get_current_value()
		if self.frame < self.length:
			pyglet.clock.schedule_once(self.advance_frame, 1/60.0)

		


class Widget(object):
	def __init__(self, parent=None):
		self.parent = parent
		self.animations = []
		self.setup()
		
	def setup(self):
		pass
		
	def draw(self):
		pass
		
	def add_animation(self, label, prop, to , timestep, length):
		anim = Animation(self, label, prop, to, timestep, length)
		self.animations.append(anim)
		return anim
		
	def start_animations(self, label='all'):
		for anim in self.animations:
			if anim.label == label or label == 'all':
				anim.reset()
				anim.start()
		


class MTWidget(Widget):
	def __init__(self, parent=None):
		Widget.__init__(self, parent)
                self.color = (1.0,1.0,1.0)
	
	def on_touch_down(self, touches, touchID, x, y):
		#print "touchdown"
		pass
		
	def on_touch_move(self, touches, touchID, x, y):
		pass

	def on_touch_up(self, touches, touchID, x, y):
		pass
	
#------ Object --- by Felipe Carvalho
	
	def on_object_down(self, touches, touchID,id, x, y,angle):
	    pass
		
	def on_object_move(self, touches, touchID,id, x, y,angle):
		pass

	def on_object_up(self, touches, touchID,id, x, y,angle):
		pass				



class TouchDisplay(MTWidget):
	def __init__(self, parent=None):
		Widget.__init__(self, parent)
		self.touches = {}
		
	def draw(self):
		for id in self.touches:
			glColor4f(1.0,1.0,1.0,0.4)
			drawCircle(pos=self.touches[id], radius=10)
	
	def on_touch_down(self, touches, touchID, x, y):
		self.touches[touchID] = (x,y)
		
	def on_touch_move(self, touches, touchID, x, y):
		self.touches[touchID] = (x,y)
	def on_touch_up(self, touches, touchID, x, y):
		del self.touches[touchID]
		
		
		
class Container(MTWidget):
	def __init__(self, children=[], parent=None, layers=1):
		self.parent = parent
                self.layers = []
                self.obj = []
                for i in range(layers):
                    self.layers.append([])
		    
		for c in children:
			self.add_widget(c)
                    
	def add_widget(self,w, z=0,type='cur'):
		if  type == 'cur':
		  self.layers[z].append(w)
		elif type == 'obj':
		    self.obj.append(w)
		
	def draw(self):
                for l in self.obj:
                            l.draw()		
                for l in self.layers:
                    for w in l:
                            w.draw()
	def on_touch_down(self, touches, touchID, x, y):
		for l in self.layers:
                    for w in reversed(l):
                        if w.on_touch_down(touches, touchID, x, y):
                            break
		
	def on_touch_move(self, touches, touchID, x, y):
		for l in self.layers:
                    for w in reversed(l):
                        if w.on_touch_move(touches, touchID, x, y):
                            break

	def on_touch_up(self, touches, touchID, x, y):
		for l in self.layers:
                    for w in reversed(l):
                        if w.on_touch_up(touches, touchID, x, y):
                            break
                           
#------ Object --- by Felipe Carvalho

	def on_object_down(self, touches, touchID,id, x, y,angle):
		for l in self.obj:
                        if l.on_object_down(touches, touchID,id, x, y,angle):
                            break
		
	def on_object_move(self, touches, touchID,id, x, y,angle):
		for l in self.obj:
                        if l.on_object_move(touches, touchID,id, x, y,angle):
                            break

	def on_object_up(self, touches, touchID,id, x, y,angle):
		for l in self.obj:
                        if l.on_object_up(touches, touchID,id, x, y,angle):
                            break


class RectangularWidget(MTWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		MTWidget.__init__(self,parent)
		self.x, self.y = pos
		self.width, self.height = size
		
	def draw(self):
		drawRectangle((self.x, self.y) ,(self.width, self.height))
                
        
		
	def collidePoint(self, x,y):
		if( x > self.x  and x < self.x + self.width and
		    y > self.y and y < self.y + self.height  ):
			return True


		
class DragableWidget(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)
		self.state = ('normal', None)
	
		
	def on_touch_down(self, touches, touchID, x, y):
		if self.collidePoint(x,y):
			self.state = ('dragging', touchID, x, y)
			return True
	def on_touch_move(self, touches, touchID, x, y):
		if self.state[0] == 'dragging' and self.state[1]==touchID:
			self.x, self.y = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
			self.state = ('dragging', touchID, x, y)
                        return True
	def on_touch_up(self, touches, touchID, x, y):
		if self.state[1] == touchID:
			self.state = ('normal', None)
                        return True
		


class Button(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)

		self.state = ('normal', 0)
		self.clickActions = []

		
	def draw(self):
		if self.state[0] == 'down':
			glColor4f(0.5,0.5,0.5,0.5)
			drawRectangle((self.x,self.y) , (self.width, self.height))
		else:
			glColor4f(0.7,0.7,0.7,0.5)
			drawRectangle((self.x,self.y) , (self.width, self.height))

		
	def on_touch_down(self, touches, touchID, x, y):
		if self.collidePoint(x,y):
			self.state = ('down', touchID)
			return True
	def on_touch_move(self, touches, touchID, x, y):
		if self.state[1] == touchID and not self.collidePoint(x,y):
			self.state = ('normal', 0)
                        return True
	def on_touch_up(self, touches, touchID, x, y):
		#print x,y , self.collidePoint(x,y)
		if self.state[1] == touchID and self.collidePoint(x,y):
			self.state = ('normal', 0)
			for callback in self.clickActions:
				callback()
			return True
                

class ImageButton(Button):
    def __init__(self, image_file, parent=None, pos=(0,0), size=(1,1), scale = 1.0):
        Button.__init__(self,parent,pos,size)
        img = pyglet.image.load(image_file)

        self.image = pyglet.sprite.Sprite(img)
        self.image.x, self.image.y = self.x, self.y
        self.scale =  scale
        self.image.scale = self.scale
        self.width, self.height = (self.image.width, self.image.height)
                       
    def draw(self):
        self.image.x, self.image.y = (self.x, self.y)
        self.image.scale = self.scale
        self.width, self.height = (self.image.width, self.image.height)
        self.image.draw()


from math import sqrt
class ZoomableWidget(RectangularWidget):
	def __init__(self, parent=None, pos=(0,0), size=(100,100)):
		RectangularWidget.__init__(self,parent, pos, size)

                self.rotation = self._rotation = self._oldrotation = 0.0 
                self.translation = self._translation = Vector(pos[0],pos[1])
                self.zoom = self._zoom = 1.0

                self.touchDict = {}                
                self.original_points = [Vector(0,0),Vector(0,0)]
                self.originalCenter = Vector(0,0)
                self.newCenter = Vector(0,0)
                
                
        
        def draw_widget(self):
            drawRectangle((-0.5, -0.5) ,(1, 1))
        
        def draw(self):
		
		#glPushMatrix()
		#radius = sqrt(self.width*self.width + self.height*self.height)/2 *self.zoom
		#drawCircle((self.translation[0], self.translation[1]) ,radius=radius, color=(1.0,.0,.0))
		#glPopMatrix()
		
                glPushMatrix()
                glTranslatef(self.translation[0], self.translation[1], 0)
                glRotatef(self.rotation , 0, 0, 1)
                glScalef(self.zoom, self.zoom, 1)
                glScalef(self.width, self.height, 1)
                self.draw_widget()
                glPopMatrix()


        def collidePoint(self, x,y):
            radius = sqrt(self.width*self.width + self.height*self.height)/2 *self.zoom
	    dist = Length(self.translation - Vector(x,y))
	    if radius >= dist:
		return True
	    else:
		return False
                
        def getAngle(self, x,y):
                        if (x == 0.0):
                                if(y < 0.0):  return 270
                                else:         return 90
                        elif (y == 0):
                                if(x < 0):  return 180
                                else:       return 0
                        if ( y > 0.0):
                                if (x > 0.0): return math.atan(y/x) * math.pi
                                else:         return 180.0-math.atan(y/-x) * math.pi
                        else:
                                if (x > 0.0): return 360.0-math.atan(-y/x) * math.pi
                                else:         return 180.0+math.atan(-y/-x) * math.pi
                
		
	def on_touch_down(self, touches, touchID, x, y):
		if not self.collidePoint(x,y):
			return False
		
                if len(self.touchDict) == 1:
                    print 'rotated'
                    self.rotation +=180
                    self._oldrotation +=180
                    
                if len(self.touchDict) < 2:
                        v = Vector(x,y)
                        self.original_points[len(self.touchDict)] = v
                        self.touchDict[touchID] = v
                        
                return True
                        
     
                

	def on_touch_move(self, touches, touchID, x, y):                
                if len(self.touchDict) == 1 and touchID in self.touchDict:
                        self.translation = Vector(x,y) - self.original_points[0] + self._translation
                        
                if len(self.touchDict) == 2 and touchID in self.touchDict:
                        points = self.touchDict.values()                       

                        #scale
                        distOld = Distance(self.original_points[0], self.original_points[1])
                        distNew = Distance(points[0], points[1])
                        self.zoom = distNew/distOld * self._zoom
                
                        #translate
                        self.originalCenter = self.original_points[0] + (self.original_points[1] - self.original_points[0])*0.5
                        self.newCenter = points[0] + (points[1] - points[0])*0.5
                        self.translation = (self.newCenter - self.originalCenter)  + self._translation
                       
                        #rotate
                        v1 = self.original_points[1] - self.original_points[0]
                        v2 = points[0] - points[1]
                        if((v1[0] < 0 and v2[0]>0) or (v1[0] > 0 and v2[0]<0)):
                            self._rotation =  ( 180+(self.getAngle(v1[0], v1[1]) - self.getAngle(v2[0], v2[1]))*-18)  %360
                        else:
                            self._rotation =  ((self.getAngle(v1[0], v1[1]) - self.getAngle(v2[0], v2[1]))*-18)  %360
                       
                        self.rotation = (self._rotation + self._oldrotation) %360

                if touchID in self.touchDict:
                        self.touchDict[touchID] = Vector(x,y)
                        
                         
	def on_touch_up(self, touches, touchID, x, y):
                if touchID in self.touchDict: #end interaction 
                        self._zoom = self.zoom
                        self._translation += self.translation - self._translation
                        self._oldrotation = (self._rotation + self._oldrotation) %360

                        self.touchDict = {}



class ZoomableImage(ZoomableWidget):
	def __init__(self, img_src,parent=None, pos=(0,0), size=(100,100)):
		ZoomableWidget.__init__(self,parent, pos, size)
                img = pyglet.image.load(img_src)
                self.image = pyglet.sprite.Sprite(img)

        def on_touch_down(self, touches, touchID, x, y):
		if ZoomableWidget.on_touch_down(self, touches, touchID, x, y):
                    self.parent.layers[0].remove(self)
                    self.parent.layers[0].append(self)
                    return True
                    
        def draw_widget(self):
            drawRectangle((-0.5, -0.5) ,(1, 1))
            glPushMatrix()
            glTranslatef(-0.5,-0.5,0)
            glScalef(1.0/self.image.height,1.0/self.image.height,1.0)
            self.image.draw()
            glPopMatrix()
	    
	    
	    
class Slider(RectangularWidget):
    def __init__(self, parent=None, min=0, max=100, pos=(10,10), size=(30,400), alignment='horizontal', padding=8, color=(0.8, 0.8, 0.4,1.0)):
	RectangularWidget.__init__(self,parent, pos, size)
	self.touchstarts = [] # only react to touch input that originated on this widget 
	self.alignment = alignment
	self.color = color
	self.padding = padding
	self.min, self.max = min, max
	self.value = self.min
	self.value = 77
    
    def draw(self):
	glEnable(GL_BLEND);
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	x,y,w,h = self.x,self.y,self.width, self.height
	p2 =self.padding/2
	#draw outer rectangle
	glColor4f(0.2,0.2,0.2,0.5)
	drawRectangle(pos=(x,y), size=(w,h))
	#draw inner rectangle
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
	if (touchID in self.touchstarts):
	    self.touchstarts.remove(touchID)
	    
	    
	    
	    
	    
class ColorPicker(RectangularWidget):
    def __init__(self, parent=None, min=0, max=100, pos=(0,0), size=(640,480),target=[]):
	RectangularWidget.__init__(self,parent, pos, size)
	self.canvas = target[0]
	self.sliders = [ Slider(max=255, size=(30,200), color=(1,0,0,1)),
			 Slider(max=255, size=(30,200), color=(0,1,0,1)),
			 Slider(max=255, size=(30,200), color=(0,0,1,1)) ] 
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
	if self.canvas: self.canvas.color = (r,g,b,1)
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
	    
	    
	    
#------ Object --- by Felipe Carvalho
 
class ObjectWidget(RectangularWidget):
    def __init__(self, parent=None, pos=(0,0), size=(100,100)):
        RectangularWidget.__init__(self,parent, pos, size)        
        
        self.state = ('normal', None)
        self.visible = False
        self.angle = 0
        self.id = 0
        
    def on_object_down(self, touches, touchID,id, x, y,angle):
            self.x ,self.y = x,y
            self.angle = angle/pi*180
            self.visible = True
            self.id = id  
            self.state = ('dragging', touchID, x, y)
            return True
    def on_object_move(self, touches, touchID,id, x, y,angle):
        if self.state[0] == 'dragging' and self.state[1]==touchID:
            self.angle = -angle/pi*180
            self.x, self.y = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
            self.id = id            
            self.state = ('dragging', touchID, x, y)
            return True
         
    def on_object_up(self, touches, touchID,id, x, y,angle):
        if self.state[1] == touchID:
            self.angle = -angle/pi*180 
            self.visible = False
            self.id = id
            self.state = ('normal', None)
            return True
        
        
    def draw(self):
        if self.visible:
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