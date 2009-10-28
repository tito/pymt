# -*- coding: utf-8 -*-

# Note: To use this example, you will need Csound and ounk.
# Csound download: http://sourceforge.net/project/showfiles.php?group_id=81968 (take the one labeled 'f' and don't install python support if asked)
# Ounk download: http://code.google.com/p/ounk/source/checkout (once you checkout, run setup.py)

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Sine Player'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This plugin is a demonstration of the integration between pymt and the ounk library.'

from pymt import *
from OpenGL.GL import *
from ounk import ounklib as ounk
import time

def pymt_plugin_activate(w, ctx):

    # A global duration of -1 will make the sound last forever
    ounk.setGlobalDuration(-1)
    # We create buses that we will use to send control data
    ounk.oscReceive(bus=['amp0','amp1','amp2','amp3','pitch0','pitch1','pitch2','pitch3'], address=['/amp0','/amp1','/amp2','/amp3','/pitch0','/pitch1','/pitch2','/pitch3'], port = 9005, portamento = 0.05)
    # We create 4 sines and associate pitch variation and amplitude variation with the corresponding buses.
    ounk.sine(pitch=[1,1,1,1], pitchVar=['pitch0','pitch1','pitch2','pitch3'], amplitudeVar=['amp0','amp1','amp2','amp3'])
    # Csound is started here
    ounk.startCsound()

    ctx.c = MTWidget()
    window_size = w.get_size()
    size = (50,350)
    sliders = []
    buttons = []
    for widget in range(4):
        sliders.append(MTSlider(min = 100, max = 1000, pos = (window_size[0]*((widget + 1)/5.) - size[0]/2., 90), size = size))
        buttons.append(MTButton(label = '', pos = (window_size[0]*((widget + 1)/5.) - size[0]/2., 30), size = (size[0], size[0])))
        ctx.c.add_widget(sliders[widget])
        ctx.c.add_widget(buttons[widget])
    s1,s2,s3,s4 = sliders
    b1,b2,b3,b4 = buttons


    # This function gets called when a slider moves, it sets the pitch of each sine.
    def on_value_change_callback(slider, value):
        ounk.sendOscControl(value, address='/pitch%d' % slider, port=9005)

    # We push the handlers and feed it with the slider number so the callback function knows which sine to work on.
    # The time.sleep seems necessary to let Csound the time to initialize itself.
    for s in range(4):
        sliders[s].push_handlers(on_value_change = curry(on_value_change_callback, s))
        time.sleep(2)
        sliders[s].value = 300

    # When the button is pressed, the amplitude is changed to 0.5
    def on_press_callback(btn, *largs):
        ounk.sendOscControl(0.5, address='/amp%d' % btn, port=9005)
        #print('Button {0} pressed'.format(btn+1))

    # When the button is released, the amplitude goes back to 0
    def on_release_callback(btn, *largs):
        ounk.sendOscControl(0, address='/amp%d' % btn, port=9005)
        #print('Button {0} released'.format(btn+1))

    # Handlers for the buttons are pushed here.
    for b in range(4):
        buttons[b].push_handlers(on_press = curry(on_press_callback, b))
        buttons[b].push_handlers(on_release = curry(on_release_callback, b))

    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)
    # Csound needs to be stopped at the end to avoid errors.
    ounk.stopCsound()

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
