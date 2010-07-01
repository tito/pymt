# -*- coding: utf-8 -*-

# Note: To use this example, you will need Csound and ounk.
# Csound download: http://sourceforge.net/project/showfiles.php?group_id=81968 (take the one labeled 'f' and don't install python support if asked)
# Ounk download: http://code.google.com/p/ounk/source/checkout (once you checkout, run setup.py)

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Matrix Sequencer'
PLUGIN_AUTHOR = 'Nathanaël Lécaudé'
PLUGIN_DESCRIPTION = 'This plugin is a demonstration of the integration between pymt and the ounk library.'

from pymt import *
from OpenGL.GL import *
from ounk import ounklib as ounk
import random, time

tt1 = 0
proc = 0
pit1 = 0

def init_ounk():
    global tt1, proc, pit1
    ounk.setGlobalDuration(-1)

    env = ounk.genAdsr(release=0.8)

    tt1 = ounk.genDataTable([1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])

    pit1 = ounk.genDataTable([1,1,1,1,.5,1,1,1,.25,1,1,1,.125,1,1,1])

    ounk.oscReceive(bus='tempo', address='/tempo', port = 9005, portamento = 0.05)
    ounk.metro(bus='metro', tempo=200, tempoVar = 'tempo')


    # solo sequence
    ounk.beginSequencer(input='metro', table=tt1)
    ounk.sequencerPitchTable(pit1)
    notes = 10
    pitchs = [random.randint(180,190)*2 for x in range(notes)]
    durs = [random.randint(1,15)*.05 for x in range(notes)]
    ounk.readTable(bus='index2', table=env, duration=durs[0])
    ounk.freqMod(pitch=pitchs, modulator=0.502, amplitude=.07, starttime=0, duration=durs, envelope=env, pan=[0,.25,.5,.75,1], index=10,indexVar='index2')
    ounk.endSequencer()

    proc = ounk.startCsound()
    time.sleep(1)
    ounk.sendOscControl(0.8, address='/tempo', port=9005)

def pymt_plugin_activate(w, ctx):
    init_ounk()
    ctx.c = MTWidget()
    temposlider = MTSlider(min = 0, max = 1, height = 125, slidercolor = (0,1,0.5,1))
    temposlider.pos = (w.width/5-temposlider.width-5, 20)
    temposlider.set_value(0.8)
    matrix = MTButtonMatrix(matrix_size = (16,1), size = (400, 25), pos = (w.width/5, 130), border = 1)
    multislider = MTMultiSlider(sliders = 16, size = (400,100), pos = (w.width/5, 20))
    ctx.c.add_widget(matrix)
    ctx.c.add_widget(multislider)
    ctx.c.add_widget(temposlider)
    w.add_widget(ctx.c)


    @matrix.event
    def on_value_change(matrix):
        table = [m[0] for m in matrix]
        ounk.reGenDataTable(tt1, table, proc)

    @multislider.event
    def on_value_change(values):
        ounk.reGenDataTable(pit1, values, proc)

    @temposlider.event
    def on_value_change(value):
        ounk.sendOscControl(value, address='/tempo', port=9005)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)
    ounk.stopCsound()

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
