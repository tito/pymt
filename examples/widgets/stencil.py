# Just a test with stacking stencil.
# InnerWindow use stencil for clipping content draw
# And Kinetic too.

# Scatter plane is here to test that stacking with different matrix
# transformation will work too.

from pymt import *

mms = MTWindow()
w = MTInnerWindow(size=(600, 600))
mms.add_widget(w)

p = MTScatterPlane()
k = MTKineticList(pos=(20, 20), size=(400, 400), w_limit=3)
p.add_widget(k)
w.add_widget(p)

d = range(0, 10)
for x in d:
    item = MTKineticItem(label=str(x))
    k.add_widget(item)

runTouchApp()
