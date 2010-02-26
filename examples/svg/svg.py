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
    ctx.c = MTKinetic()
    for svg_file in ['sun.svg', 'cloud.svg', 'ship.svg']:
        filename=join(current_dir, svg_file)
        scatter = MTScatterWidget(style={'bg-image':Svg(filename), 'bg-color': (0,0,0,0)})        
        ctx.c.add_widget(scatter)
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
