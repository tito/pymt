# -*- coding: utf-8 -*-

# Note: To use this example, you will need the pyo library.
# Download link : http://pyo.googlecode.com


# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Sine Player'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This plugin is a demonstration of the integration between pymt and the pyo library.'

from pymt import *
from OpenGL.GL import *
import pyo

# will not work if 2 app use pyo
pyo_server = pyo.Server(nchnls=2).boot()
pyo_count = 0

def pymt_plugin_activate(w, ctx):
    ctx.c = MTWidget()

    # We initialize the pyo server.
    global pyo_count
    pyo_count += 1
    if pyo_count == 1:
        pyo_server.start()

    # We create 4 lists which will contain our sliders (to control pitch),
    # buttons (to trigger the sound), pyo sine waves and fader objects.
    sliders = []
    buttons = []
    sines = []
    faders = []

    vlayouts = []

    hlayout = MTBoxLayout(spacing=w.width / 10, size=w.size)

    def resize_hlayout(w, h):
        # reajust layout when moving
        hlayout.spacing = w / 10
        hlayout.size = w, h
        hlayout.do_layout()

    w.connect('on_resize', resize_hlayout)

    # We create 4 instances of each of the above
    for widget in range(4):
        vlayouts.append(MTBoxLayout(orientation='vertical', spacing=10))
        sliders.append(MTSlider(min=100, max=1000, size_hint=(1, .9)))
        buttons.append(MTButton(label='', size_hint=(1, .1)))
        vlayouts[widget].add_widget(buttons[widget])
        vlayouts[widget].add_widget(sliders[widget])
        hlayout.add_widget(vlayouts[widget])
        faders.append(pyo.Fader(fadein = 0.5, fadeout = 0.5, dur = 0, mul = 0.25))
        sines.append(pyo.Sine(mul = faders[widget], freq = 300))
        sines[widget].out()

    ctx.c.add_widget(hlayout)

    # This function gets called when a slider moves, it sets the pitch of each sine.
    def on_value_change_callback(slider, value):
        sines[slider].freq = value

    # When the button is pressed, the fader object performs it's fade.
    def on_press_callback(btn, *largs):
        faders[btn].play()

    # When the button is released, the fader object fades back to 0.
    def on_release_callback(btn, *largs):
        faders[btn].stop()

    # We push the handlers and feed it with the slider number so the callback function knows which sine to work on.
    for s in range(4):
        sliders[s].push_handlers(on_value_change = curry(on_value_change_callback, s))
        sliders[s].value = 300

    # Handlers for the buttons are pushed here.
    for b in range(4):
        buttons[b].push_handlers(on_press = curry(on_press_callback, b))
        buttons[b].push_handlers(on_release = curry(on_release_callback, b))

    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    # pyo Server is stopped
    global pyo_count
    pyo_count -= 1
    if pyo_count == 0:
        pyo_server.stop()
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
