from pymt import *

sl = MTVectorSlider(pos=getWindow().center)

@sl.event
def on_amplitude_change(value):
    print 'Slider amplitude change', value

@sl.event
def on_angle_change(value):
    print 'Slider angle change', value

@sl.event
def on_vector_change(x, y):
    print 'Slider vector change', x, y

runTouchApp(sl)
