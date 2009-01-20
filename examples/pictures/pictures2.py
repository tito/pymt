# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Pictures'
PLUGIN_AUTHOR = 'Thomas Hansen & Sharath'
PLUGIN_DESCRIPTION = 'Demonstration of MTScatterWidget object'

from pymt import *
import os
import random
import math

def drawRectangle(pos=(0,0), size=(1.0,1.0), ):
    data = (pos[0],pos[1], pos[0]+size[0],pos[1], pos[0]+size[0], pos[1]+size[1], pos[0],pos[1]+size[1])
    draw(4, GL_QUADS, ('v2f', data))
    

class MTScatteredObj(MTScatterWidget):
    """MTScatteredObj is a zoomable Image widget with a possibility of providing rotation during spawning"""
    def __init__(self, img_src, pos=(0,0), size=(100,100), rotation=45):
        img  = pyglet.image.load(img_src)
        self.image  = pyglet.sprite.Sprite(img)
        self.aspectRatio = float(self.image.height)/float(self.image.width)
        MTScatterWidget.__init__(self, pos=pos, size=(size[0],size[0]*self.aspectRatio))
        self.rotation = rotation
        
    def draw(self):
       glPushMatrix()
       enable_blending()
       glColor4f(1,1,1,0.5)
       drawRectangle((-10,-10),(self.width+20,self.width*self.aspectRatio+20))
       glScaled(float(self.width)/float(self.image.width), float(self.width*self.aspectRatio)/float(self.image.height), 1.0)
       self.image.draw()
       glPopMatrix()

class BackgroundImage(MTWidget):
    def __init__(self, image_file, pos=(0,0), size=(1,1), scale = 1.0, **kargs):
        MTWidget.__init__(self, pos=pos, size=size, **kargs)
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
 
def pymt_plugin_activate(w, ctx):
    ctx.c = MTWidget()
    back = BackgroundImage(image_file='back.jpg',size=(1,1),scale = 1.25)
    ctx.c.add_widget(back)
    for i in range (5):
        img_src = '../pictures/images/pic'+str(i+1)+'.jpg'
        teta = float((360/5)*i*(math.pi/180))
        #print "Teta: ",teta
        x = int((550)+ (200*math.cos(teta)))
        y = int((340)+ (200*math.sin(teta)))
        print "x,y",x,y
        #x = int(random.uniform((w.width/2)-400, (w.width/2)+100))
        #y = int(random.uniform((w.height/2)-100, (w.height/2)+100))
        size = 300
        rot = (360/5)*i
        b = MTScatteredObj(img_src, (x,y),(size,size), rot)
        ctx.c.add_widget(b)
    ctx.c._set_pos((int(w.width/2),int(w.height/2)))
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    w.set_fullscreen()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)  
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
