#!/usr/bin/env python

from pymt import *


class Line(MTWidget):
	def __init__(self, fro ,to, parent=None):
		MTWidget.__init__(self, parent)
		self.fro = fro
		self.to = to
		
	def draw(self):
		x,y  = self.fro.x, self.fro.y
		xt,yt = self.to.x, self.to.y
		glColor4d(.9,.9,.9, 0.7)
		drawLine((x,y,xt,yt))


class FlowchartObject(MTScatterWidget):

	line_targets = []

	def __init__(self, pos=(0,0), size=(150,100), text="Flowchart Symbol", color=(0.3,0.3,0.5,0.9)):
		MTScatterWidget.__init__(self, pos=pos, size=size, color=color)
		FlowchartObject.line_targets.append(self)
		self.mode = 'normal'
	
	def __del__(self):
		FlowchartObject.line_targets.remove(self)


	def on_draw(self):
		if self.mode == 'lineDrawing':
			x,y  = self.x,self.y
			xt,yt = self.line_target[0],self.line_target[1]
			glColor3d(.9,.9,.9)
			drawLine((x,y, xt,yt))
		
		MTScatterWidget.on_draw(self)

	def find_target(self):
		for target in FlowchartObject.line_targets:
			if target != self:
				if target.collide_point(self.line_target[0],self.line_target[1]):
					return target
	
	def on_touch_down(self, touches, touchID, x, y):
		#if this is the third touch, start a new line
		if (len(self.touches) == 2) and self.collide_point(x,y):
			self.mode = 'lineDrawing'
			self.line_target = (x,y,touchID)
		
		MTScatterWidget.on_touch_down(self, touches, touchID, x, y)
			
		
	def on_touch_move(self, touches, touchID, x, y):                
		if self.mode == 'lineDrawing' and self.line_target[2] == touchID:
			self.line_target = (x,y,touchID) #update position of line end
			target = self.find_target()
			if (target):
				self.line_target = (target.x,target.y,touchID)
	
		MTScatterWidget.on_touch_move(self, touches, touchID, x, y)
			 
	
	def on_touch_up(self, touches, touchID, x, y):
		if self.mode == 'lineDrawing' and self.haveTouch(touchID):
				target = self.find_target()
				if (target):
					self.parent.add_widget(Line(self,target, parent=self.parent ))
		if self.haveTouch(touchID):
			self.line_target = (0,0,0)
			self.mode = 'normal'

		MTScatterWidget.on_touch_up(self, touches, touchID, x, y)        
	
        

class Oval(FlowchartObject):
	def draw(self):
		glPushMatrix()
		glTranslated(self.x, self.y, 0)
		glScaled(self.width, self.height, 1.0)
		enable_blending()
		glColor4f(*self.color)
		drawCircle(pos=(0.5,0.5), radius=0.5)
		glPopMatrix()
		drawLabel("Oval", pos=self.center)

class Box(FlowchartObject):
	def draw(self):
		glPushMatrix()
		glTranslated(self.x, self.y, 0)
		glScaled(self.width, self.height, 1.0)
		enable_blending()
		glColor4f(*self.color)
		drawRectangle(pos=(0,0), size=(1,1))
		glPopMatrix()
		drawLabel("Box", pos=self.center)

class Rhombus(FlowchartObject):
	def draw(self):
		glPushMatrix()
		glTranslated(self.x, self.y, 0)
		glScaled(self.width, self.height, 1.0)
		glTranslated(0.5,0.5, 0)
		glRotated(45, 0,0,1)
		enable_blending()
		glColor4f(*self.color)
		drawRectangle(pos=(-0.5,-0.5), size=(1,1))
		glPopMatrix()
		drawLabel("Rhombus", pos=self.center)




class CreatorWidget(MTContainer):
    def __init__(self, parent=None, pos=(100,100)):
        MTContainer.__init__(self,parent=parent)
        self.pos=pos
        
        self.squareButton  = MTButton(label="Box", pos=(20,40), size=(80,50))
        self.ovalButton    = MTButton(label="Oval", pos=(20,100), size=(80,50))
        self.rhombusButton = MTButton(label="Rhombus", pos=(20,160), size=(80,50))
        
        def newBox(touchID, x,y):
			parent.add_widget(Box(pos=(200,80), size=(150,120), color=(1,.3,.3,.8)))
        def newOval(touchID, x,y):
            parent.add_widget(Oval(pos=(200,140), size=(150,120), color=(.3,1,.3,.8)))
        def newRhombus(touchID, x,y):
            parent.add_widget(Rhombus(pos=(200,200), size=(150,120), color=(.3,.3,1,.8)))
            
            
        self.squareButton.push_handlers(on_click=newBox)
        self.ovalButton.push_handlers(on_click=newOval)
        self.rhombusButton.push_handlers(on_click=newRhombus)
        
        self.add_widget(self.squareButton)
        self.add_widget(self.ovalButton)
        self.add_widget(self.rhombusButton)
        
        
    
    
    

if __name__ == "__main__":
    c = MTWidget()
    w = CreatorWidget(parent=c)
    c.add_widget(w)
    

    
    #c.add_widget( MTScatterWidget(pos=(400,200),id="test") )
    
    win = MTWindow()
    win.add_widget(c)
    #win.set_fullscreen()
    runTouchApp()
