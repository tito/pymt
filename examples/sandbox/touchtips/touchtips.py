# -*- coding: utf-8 -*-
from pymt import *
import pyglet

# PYMT Plugin integration
IS_PYMT_PLUGIN = False
PLUGIN_TITLE = 'Touch Tips'
PLUGIN_AUTHOR = 'Riley Dutton'
PLUGIN_DESCRIPTION = 'An example of TouchTips, a system for showing hints to users of a multi-touch table regarding appropriate gestures for an object.'

def pymt_plugin_activate(w, ctx):
    Tips = MTTouchTip()
    
    ctx.c = MTKinetic()
    
    test = MTAnimatedGif(filename="test.gif")
    test.scale = 3.0
    test.pos = (300, 300)
    
    test2 = MTScatterImage(filename='../../pictures/images/pic1.jpg', pos=(200, 600), rotation=60, size=(500, 500))
    
    test3 = MTImageButton(filename="../../pictures/images/pic2.jpg", pos=(600, 200), scale=0.50)
    
    ctx.c.add_widget(test)
    ctx.c.add_widget(test2)
    ctx.c.add_widget(test3)
    ctx.c.add_widget(Tips)
    w.add_widget(ctx.c)
    Tips.attach(test, "tap", delay=5.0)
    Tips.attach(test2, "pinch", delay=5.0, rotation=-60)
    Tips.attach(test3, "tap", delay=0.0)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
