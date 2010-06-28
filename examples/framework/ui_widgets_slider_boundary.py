from pymt import *

sl = MTBoundarySlider(value=50)

@sl.event
def on_value_change(vmin, vmax):
    print 'Slider values change: ', vmin, ' - ', vmax

runTouchApp(sl)
