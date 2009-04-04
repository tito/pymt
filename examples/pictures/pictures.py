# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Picture Viewer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'Demonstration of MTScatterImage object'

from pymt import *
import os
import random

def pymt_plugin_activate(w, ctx):
    ctx.c = MTKinetic()
    for i in range (10):
        img_src = '../pictures/bilder/testpic'+str(i+1)+'.jpg'
        x = int(random.uniform(100, w.width-100))
        y = int(random.uniform(100, w.height-100))
        size = random.uniform(0.5, 4.1)*100
        rot = random.uniform(0, 360)
        b = MTScatterImage(filename=img_src, pos=(x,y), size=(size,size), rotation=rot)
        ctx.c.add_widget(b)
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
