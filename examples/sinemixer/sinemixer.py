# -*- coding: utf-8 -*-
# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Sine Player'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This plugin is a demonstration of the integration between pymt and the ounk library.'

from pymt import *
from pyglet.gl import *

def pymt_plugin_activate(w, ctx):
    ctx.c = MTWidget()
    window_size = w.get_size()
    size = (50,350)
    sliders = []
    buttons = []
    for widget in range(4):
        sliders.append(MTSlider(pos = (window_size[0]*((widget + 1)/5.) - size[0]/2., 90), size = size))
        buttons.append(MTToggleButton(label = 'Hello', pos = (window_size[0]*((widget + 1)/5.) - size[0]/2., 30), size = (size[0], size[0])))
        ctx.c.add_widget(sliders[widget])
        ctx.c.add_widget(buttons[widget])
    s1,s2,s3,s4 = sliders
    b1,b2,b3,b4 = buttons
    
    @s1.event
    def on_value_change(value):
        #print('Slider1',value)
        print(b1.get_state())

    @s2.event
    def on_value_change(value):
        #print('Slider2',value)
        b1.set_state('normal')
    
    @s3.event
    def on_value_change(value):
        #print('Slider3',value)
        b1.set_state('down')
    
    @s4.event
    def on_value_change(value):
        print('Slider4',value)
   
    def on_release_callback(btn, touchID, x,y):
        print('Button {0} released'.format(btn+1))
        
    def on_press_callback(btn, touchID, x, y):
        print('Button {0} pressed'.format(btn+1))
    
    for b in range(4):
        buttons[b].push_handlers(on_press = curry(on_press_callback, b))
        buttons[b].push_handlers(on_release = curry(on_release_callback, b))
    
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
