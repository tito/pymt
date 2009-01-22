# -*- coding: utf-8 -*-

# Note: To use this example, you will need Csound and ounk.
# Csound download: http://sourceforge.net/project/showfiles.php?group_id=81968
# Ounk download: http://code.google.com/p/ounk/source/checkout (once you checkout, run setup.py)

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Sine Player'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This plugin is a demonstration of the integration between pymt and the ounk library.'

from pymt import *
from pyglet.gl import *
from ounk import ounklib as ounk
import time

def pymt_plugin_activate(w, ctx):
    ounk.setGlobalDuration(-1)
    ounk.oscReceive(bus=['amp0','amp1','amp2','amp3','pitch0','pitch1','pitch2','pitch3'], adress=['/amp0','/amp1','/amp2','/amp3','/pitch0','/pitch1','/pitch2','/pitch3'], port = 9005, portamento = 0.05)
    ounk.sine(pitch=[1,1,1,1], pitchVar=['pitch0','pitch1','pitch2','pitch3'], amplitudeVar=['amp0','amp1','amp2','amp3'])
    ounk.startCsound()
    time.sleep(1.5)
    
    ctx.c = MTWidget()
    window_size = w.get_size()
    size = (50,350)
    sliders = []
    buttons = []
    for widget in range(4):
        sliders.append(MTSlider(min = 100, max = 1000, pos = (window_size[0]*((widget + 1)/5.) - size[0]/2., 90), size = size))
        sliders[widget].set_value(300)
        buttons.append(MTButton(label = '', pos = (window_size[0]*((widget + 1)/5.) - size[0]/2., 30), size = (size[0], size[0])))
        ctx.c.add_widget(sliders[widget])
        ctx.c.add_widget(buttons[widget])
    s1,s2,s3,s4 = sliders
    b1,b2,b3,b4 = buttons
    
    # Force init of the pitches
    for val in range(4):
        ounk.sendOscControl(300, adress='/pitch{0}'.format(val), port=9005)
    
    @s1.event
    def on_value_change(value):
        ounk.sendOscControl(value, adress='/pitch0', port=9005)
        print('Slider1',value)

    @s2.event
    def on_value_change(value):
        ounk.sendOscControl(value, adress='/pitch1', port=9005)
        print('Slider2',value)
    
    @s3.event
    def on_value_change(value):
        ounk.sendOscControl(value, adress='/pitch2', port=9005)
        print('Slider3',value)
    
    @s4.event
    def on_value_change(value):
        ounk.sendOscControl(value, adress='/pitch3', port=9005)
        print('Slider4',value)
   
    def on_release_callback(btn, touchID, x,y):
        ounk.sendOscControl(0, adress='/amp{0}'.format(btn), port=9005)
        print('Button {0} released'.format(btn+1))
        
    def on_press_callback(btn, touchID, x, y):
        ounk.sendOscControl(0.5, adress='/amp{0}'.format(btn), port=9005)
        print('Button {0} pressed'.format(btn+1))
    
    for b in range(4):
        buttons[b].push_handlers(on_press = curry(on_press_callback, b))
        buttons[b].push_handlers(on_release = curry(on_release_callback, b))
    
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)
    ounk.stopCsound()

if __name__ == '__main__':
    w = MTWindow()
    #w.set_fullscreen()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
