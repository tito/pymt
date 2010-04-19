# example with a scatter plane + multiple circular slider
# add a css to see bounding box of circular slider

from pymt import *

css_add_sheet('circularslider { draw-background: 1; }')

s = MTScatterPlane()

m = MTBoxLayout(pos=(100,100))
c = MTCircularSlider(radius=100.0, rotation=200, value=50, thickness=20)
m.add_widget(c)
c2 = MTCircularSlider(radius=50.0, rotation=90, value=75)
m.add_widget(c2)
c3 = MTCircularSlider(radius=80.0, value=25, padding=8, thickness=50)
c3.value = 100
c.value = 25

c.connect('on_value_change', c2, 'value')
c.connect('on_value_change', c3, 'value')

m.add_widget(c3)
s.add_widget(m)

runTouchApp(s)
