from pymt import *

# create a slider from 0.-1.
sl = MTSlider(min=0., max=1.)

@sl.event
def on_value_change(value):
    print 'Slider value change', value

runTouchApp(sl)
