# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Pictures'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'Demonstration of MTScatterImage object'

from pymt import *
import os
import random

class MTScatteredObj(MTScatterImage):
    """MTScatteredObj is a zoomable Image widget with a possibility of providing rotation during spawning"""
    def __init__(self, img_src, pos=(0,0), size=(100,100), rotation=45):
        MTScatterImage.__init__(self,img_src,pos,size)
        self.rotation = rotation

def pymt_plugin_activate(w, ctx):
    ctx.c = MTWidget()
    for i in range (10):
        img_src = '../pictures/bilder/testpic'+str(i+1)+'.jpg'
        x = int(random.uniform(100, w.width-100))
        y = int(random.uniform(100, w.height-100))
        size = random.uniform(0.5, 4.1)*100
        rot = random.uniform(0, 360)
        b = MTScatteredObj(img_src, (x,y),(size,size), rot)
        ctx.c.add_widget(b)
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    #w.set_fullscreen()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
