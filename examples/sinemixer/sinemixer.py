# -*- coding: utf-8 -*-

# Note: To use this example, you will need Csound and ounk.
# Csound download: http://sourceforge.net/project/showfiles.php?group_id=81968 (take the one labeled 'f' and don't install python support if asked)
# Ounk download: http://code.google.com/p/ounk/source/checkout (once you checkout, run setup.py)

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Sine Player'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This plugin is a demonstration of the integration between pymt and the pyo library.'

from pymt import *
from OpenGL.GL import *
from pyo import *

def pymt_plugin_activate(w, ctx):
    ctx.c = MTWidget()
    
    # We initialize the pyo server.
    s = Server(nchnls = 2).boot()
    s.start()
    
    widget_size = (50, w.size[1] / 2)
    
    # We create 4 lists which will contain our sliders (to control pitch), buttons (to trigger the sound), pyo sine waves and fader objects.
    sliders = []
    buttons = []
    sines = []
    faders = []
    
    # We create 4 instances of each of the above
    for widget in range(4):
        sliders.append(MTSlider(min = 100, max = 1000, pos = (w.size[0]*((widget + 1)/5.) - widget_size[0]/2., 90), size = widget_size))
        buttons.append(MTButton(label = '', pos = (w.size[0]*((widget + 1)/5.) - widget_size[0]/2., 30), size = (widget_size[0], widget_size[0])))
        faders.append(Fader(fadein = 0.5, fadeout = 0.5, dur = 0, mul = 0.25))
        sines.append(Sine(mul = faders[widget], freq = 100))
        sines[widget].out()
        ctx.c.add_widget(sliders[widget])
        ctx.c.add_widget(buttons[widget])
    s1,s2,s3,s4 = sliders
    b1,b2,b3,b4 = buttons

    # This function gets called when a slider moves, it sets the pitch of each sine.
    def on_value_change_callback(slider, value):
        sines[slider].freq = value

    # When the button is pressed, the amplitude is changed to 0.5
    def on_press_callback(btn, *largs):
        faders[btn].play()

    # When the button is released, the amplitude goes back to 0
    def on_release_callback(btn, *largs):
        faders[btn].stop()
    
    # We push the handlers and feed it with the slider number so the callback function knows which sine to work on.
    for s in range(4):
        sliders[s].push_handlers(on_value_change = curry(on_value_change_callback, s))
        time.sleep(2)
        sliders[s].value = 300
        
    # Handlers for the buttons are pushed here.
    for b in range(4):
        buttons[b].push_handlers(on_press = curry(on_press_callback, b))
        buttons[b].push_handlers(on_release = curry(on_release_callback, b))
        
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
