from pymt import *
import os
import random
from pyglet.media import *

class MTVideoObj(MTScatterImage):
    """MTScatteredObj is a zoomable Image widget with a possibility of providing rotation during spawning"""
    def __init__(self, img_src="..\pictures\drawing.jpg",parent=None, pos=(0,0), size=(0,0), rotation=0):
        MTScatterImage.__init__(self,img_src,parent,pos,size)
        self.rotation = rotation
        self.x = pos[0]
        self.y = pos[1]
        self.player = Player()
        self.source = pyglet.media.load('video.avi')
        self.player.queue(self.source)
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
  
    def play(self):
        self.player.play()

    def draw(self):
        glPushMatrix()
        glTranslated(self.x, self.y, 0)
        glRotated(self.rotation, 0,0,1)
        glColor3d(1,1,1)
        glScalef(self.zoom, self.zoom, 1)		
        self.player.get_texture().blit(0,0)
        glPopMatrix()	

		
    """def on_draw(self):

        glScalef(self.zoom, self.zoom, 1)		
        self.draw()
        glPopMatrix()		
	
        #self.image  = self.player.get_texture().blit(0,0)
        glPushMatrix()
        glTranslated(self.x, self.y, 0)
        #glScaled(float(self.width)/self.source.width, float(self.height)/self.source.height, 2.0)
        self.player.get_texture().blit(self.x,self.y)#self.image.draw()
        glPopMatrix()
		
   def on_draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)

        glScalef(self.zoom, self.zoom, 1)
        glTranslatef(-self.x, -self.y, 0)
        glTranslatef(-self.width/2, -self.height/2, 0)
        #glColor3d(0,0,0)
        self.draw()
        glPopMatrix()		
"""

if __name__ == '__main__':
    w = MTWindow()
    w.set_fullscreen()
    video = MTVideoObj()
    w.add_widget(video)
    video.play()
    runTouchApp()

