from pymt import *

m = MTWindow()

o = MTVectorSlider(pos=(m.width/2, m.height/2))
m.add_widget(o)

runTouchApp()
