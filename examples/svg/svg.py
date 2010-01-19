# -*- coding: utf-8 -*-
from pymt import *
import os
from os.path import join

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'SVG Viewer'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This is an example of Scalable Vector Graphics using the Squirtle library for pyglet.'

current_dir = os.path.dirname(__file__)

def pymt_plugin_activate(w, ctx):
    sun = MTScatterSvg(filename=join(current_dir, 'sun.svg'), pos=(200,200))
    cloud = MTScatterSvg(filename=join(current_dir, 'cloud.svg'), pos=(50,100))
    ship = MTScatterSvg(filename=join(current_dir, 'ship.svg'), pos=(280,100))
    ctx.c = MTKinetic()
    ctx.c.add_widget(sun)
    ctx.c.add_widget(cloud)
    ctx.c.add_widget(ship)
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
