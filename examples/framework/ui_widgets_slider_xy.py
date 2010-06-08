
from pymt import *

# create a slider from 0.-1.
sl = MTXYSlider()

@sl.event
def on_value_change(x, y):
    print 'Slider value change', x, y

runTouchApp(sl)
