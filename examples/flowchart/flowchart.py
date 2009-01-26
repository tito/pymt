#!/usr/bin/env python

from pymt import *


class Line(MTWidget):
    def __init__(self, fro ,to):
        MTWidget.__init__(self)
        self.fro = fro
        self.to = to

    def draw(self):
        x,y  = self.fro.center
        xt,yt = self.to.center
        glColor4d(.9,.9,.9, 0.7)
        drawLine((x,y,xt,yt))



class FlowchartText(MTTextInput):
    def __init__(self, label="text input", pos=(0,0), size=(100,100)):
        super(FlowchartText,self).__init__(label=label, pos=pos, size=size,color=(1,1,1,0.3))

    def draw(self):
        enable_blending()
        if self.state[0] == 'down':
            glColor4f(0.5,0.5,0.5,0.5)
            drawRoundedRectangle((self.x,self.y) , (self.width, self.height))
        else:
            glColor4f(*self.color)
            drawRoundedRectangle((self.x,self.y) , (self.width, self.height))
        disable_blending()
        self.label_obj.draw()

class FlowchartObject(MTScatterWidget):

    line_targets = []

    def __init__(self, pos=(0,0), size=(150,100), text="Flowchart Symbol", color=(0.3,0.3,0.5,0.9)):
        MTScatterWidget.__init__(self, pos=pos, size=size, color=color)
        FlowchartObject.line_targets.append(self)
        self.mode = 'normal'
        self.textinput = FlowchartText(size=(40,40))
        self.textinput.pos = (self.width/2-self.textinput.width/2, self.height/2-self.textinput.height/2)
        self.add_widget(self.textinput)

    def __del__(self):
        FlowchartObject.line_targets.remove(self)



    def on_draw(self):
        if self.mode == 'lineDrawing':
            x,y  = self.center
            xt,yt = self.line_target[0],self.line_target[1]
            glColor3d(.9,.9,.9)
            drawLine((x,y, xt,yt))

        self.textinput.pos = (self.width/2-self.textinput.width/2, self.height/2-self.textinput.height/2)
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

        return MTScatterWidget.on_touch_down(self, touches, touchID, x, y)


    def on_touch_move(self, touches, touchID, x, y):
        if self.mode == 'lineDrawing' and self.line_target[2] == touchID:
            self.line_target = (x,y,touchID) #update position of line end
            target = self.find_target()
            if (target):
                self.line_target = (target.center[0],target.center[1],touchID)

        return MTScatterWidget.on_touch_move(self, touches, touchID, x, y)


    def on_touch_up(self, touches, touchID, x, y):
        if self.mode == 'lineDrawing' and self.haveTouch(touchID):
                target = self.find_target()
                if (target):
                    print self.parent
                    self.parent.add_widget(Line(self,target))
        if self.haveTouch(touchID):
            self.line_target = (0,0,0)
            self.mode = 'normal'

        return MTScatterWidget.on_touch_up(self, touches, touchID, x, y)



class Oval(FlowchartObject):
    def draw(self):
        glPushMatrix()
        glScaled(self.width, self.height, 1.0)
        enable_blending()
        glColor4f(*self.color)
        drawCircle(pos=(0.5,0.5), radius=0.5)
        glPopMatrix()
        ##drawLabel("Oval", pos=(self.width/2, self.height/2))

class Box(FlowchartObject):
    def draw(self):
        glPushMatrix()
        #glScaled(self.width, self.height, 1.0)
        enable_blending()
        glColor4f(*self.color)
        drawRoundedRectangle(pos=(0,0), size=self.size)
        glPopMatrix()
        #drawLabel("Box", pos=(self.width/2, self.height/2))

class Rhombus(FlowchartObject):
    def draw(self):
        glPushMatrix()
        glScaled(self.width, self.height, 1.0)
        glTranslated(0.5,0.75, 0)
        glRotated(45, 0,0,1)
        enable_blending()
        glColor4f(*self.color)
        drawRectangle(pos=(-0.5,-0.5), size=(0.7,0.7))
        glPopMatrix()
        #drawLabel("Rhombus", pos=(self.width/2, self.height/2*0.6))




class CreatorWidget(MTWidget):
    def __init__(self,  pos=(100,100)):
        MTWidget.__init__(self)
        self.pos=pos

        self.squareButton  = MTButton(label="Box", pos=(20,40), size=(80,50))
        self.ovalButton    = MTButton(label="Oval", pos=(20,100), size=(80,50))
        self.rhombusButton = MTButton(label="Rhombus", pos=(20,160), size=(80,50))

        def newBox(touchID, x,y):
            self.parent.add_widget(Box(pos=(200,80), size=(150,120), color=(.7,.3,.3,.8)))
        def newOval(touchID, x,y):
            self.parent.add_widget(Oval(pos=(200,140), size=(150,120), color=(.3,.7,.3,.8)))
        def newRhombus(touchID, x,y):
            self.parent.add_widget(Rhombus(pos=(200,200), size=(150,120), color=(.3,.3,.7,.8)))


        self.squareButton.push_handlers(on_release=newBox)
        self.ovalButton.push_handlers(on_release=newOval)
        self.rhombusButton.push_handlers(on_release=newRhombus)

        self.add_widget(self.squareButton)
        self.add_widget(self.ovalButton)
        self.add_widget(self.rhombusButton)






if __name__ == "__main__":

    win = MTWindow()
    c = MTScatterWidget(size=(win.width, win.height))
    w = CreatorWidget()
    c.add_widget(w)
    win.add_widget(c)
    #win.set_fullscreen()
    runTouchApp()
