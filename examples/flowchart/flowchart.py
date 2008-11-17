#!/usr/bin/env python

from pymt import *

class LineTool(ZoomableWidget):
    def __init__(self, pos=(0,0), size=(100,100)):
        ZoomableWidget.__init__(self, pos=pos, size=size)
    
            
            
    def draw_widget(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glColor4f(0.7,0.7,0.7, 0.2)
        drawCircle((0,0), radius=0.5)
	glColor4f(0.4,0.7,0.4, 0.4)
        drawCircle((0,0), radius=0.3)
        glDisable(GL_BLEND)

collision_targets = []

class Line(MTWidget):
    def __init__(self, fro ,to, parent=None):
        print 'creating line'
        MTWidget.__init__(self, parent)
        self.fro = fro
        self.to = to
        
    def draw(self):
        print 'drawing Line'
        x,y  = self.fro.translation[0], self.fro.translation[1]
        xt,yt = self.to.translation[0], self.to.translation[1]
        drawLine((x,y,xt,yt))


class Symbol(ZoomableWidget):
    def __init__(self, pos=(0,0), size=(150,100), text="Flowchart Symbol", color=(0.3,0.3,0.5,0.9)):
        ZoomableWidget.__init__(self, pos=pos, size=size)
        self.color=color
        self.mode='normal'
        collision_targets.append(self)
        self.label = label = pyglet.text.Label(text,
                          font_name='Times New Roman',
                          font_size=size[0] /4,
                          x=0,y=0,
                          anchor_x='center', anchor_y='center')
    
    def draw(self):
        ZoomableWidget.draw(self)
        if self.mode == 'lineDrawing':
            x,y  = self.translation[0],self.translation[1]
            xt,yt = self.line_target[0],self.line_target[1]
            drawLine((x,y, xt,yt))
    
    def drawLabel(self):
        glPushMatrix()
        s = 1.0/(self.width*self.zoom) *self.zoom *0.3
        glScaled(s,s*self.width/self.height,1)
        self.label.draw()
	glPopMatrix()
        
    def on_touch_down(self, touches, touchID, x, y):
        #print 'third touch?  ', len(self.touchDict)
        if (len(self.touchDict) == 2) and self.collidePoint(x,y):
            print 'third touch'
            self.mode = 'lineDrawing'
            self.line_target = (x,y,touchID)
        else:
            ZoomableWidget.on_touch_down(self, touches, touchID, x, y)
            
            
    def checkCollisions(self):
        for target in collision_targets:
            if target != self:
                if target.collidePoint(self.line_target[0],self.line_target[1]):
                    return target
            
    def on_touch_move(self, touches, touchID, x, y):                
        if self.mode == 'lineDrawing':
            if self.line_target[2] == touchID:
                self.line_target = (x,y,touchID)
                t = self.checkCollisions()
                if (t):
                    self.line_target = (t.translation[0],t.translation[1],touchID)
        else:
            ZoomableWidget.on_touch_move(self, touches, touchID, x, y)
             
    
    def on_touch_up(self, touches, touchID, x, y):
        if self.mode == 'lineDrawing' and self.line_target[2] == touchID:
                t = self.checkCollisions()
                if (t):
                    print 'adding line', c.layers[0]
                    c.add_widget(Line(self,t),z=0)
                self.line_target = (0,0,0)
                self.mode = 'normal'
            #elif (touchID in self.touchDict)
        else:
            self.line_target = (0,0,0)
            self.mode = 'normal'
            ZoomableWidget.on_touch_up(self, touches, touchID, x, y)
        
        
        

        
class Box(Symbol):
    def draw_widget(self):
	glColor4f(*self.color)
        drawRectangle((-.5,-.5), (1.0,1.0))
        self.drawLabel()

class Rhombus(Symbol):
    def draw_widget(self):
	glColor4f(*self.color)
        drawTriangle((0.0,0), 1.0, 0.5)
        drawTriangle((0.0,0), 1.0, -0.5)
        self.drawLabel()

class Oval(Symbol):
    def draw_widget(self):
        x,y = self.translation[0], self.translation[1]
        glPushMatrix()
        #glTranslatef(x,y,0)
        glScalef(1.0, float(self.height)/self.width, 1.0)
	glColor4f(0.4,0.7,0.4, 0.4)
	glColor4f(*self.color)
        drawCircle((0,0), radius=0.5)
        glPopMatrix()
        self.drawLabel()






class CreatorWidget(Container):
    def __init__(self, parent=None, pos=(100,100)):
        Container.__init__(self,parent=parent)
        self.pos=pos
        
        self.squareButton = Button(pos=(50,80), size=(80,80))
        self.ovalButton = Button(pos=(50,180), size=(80,80))
        self.rhombusButton = Button(pos=(50,280), size=(80,80))
        
        def newBox(touchID, x,y):
            parent.add_widget( Box(pos=(100,80), size=(150,120)), z=1 )
        def newOval(touchID, x,y):
            parent.add_widget(Oval(pos=(100,180), size=(150,120)), z=1)
        def newRhombus(touchID, x,y):
            parent.add_widget(Rhombus(pos=(200,280), size=(150,120)), z=1)
            
            
        self.squareButton.push_handlers(on_click=newBox)
        self.ovalButton.push_handlers(on_click=newOval)
        self.rhombusButton.push_handlers(on_click=newRhombus)
        
        self.add_widget(self.squareButton)
        self.add_widget(self.ovalButton)
        self.add_widget(self.rhombusButton)
        
        
    
    
    

if __name__ == "__main__":
    c = Container(layers=2)
    w = CreatorWidget(parent=c)
    c.add_widget(w,z=1)
    
    tool = LineTool()
    c.add_widget(tool, z=1)
    
    win = UIWindow(c)
    #win.set_fullscreen()
    runTouchApp()