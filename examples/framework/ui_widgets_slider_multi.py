from pymt import *

sl = MTMultiSlider(init_value=0.1)

@sl.event
def on_value_change(values):
    print 'Slider values change: ', values

runTouchApp(sl)
