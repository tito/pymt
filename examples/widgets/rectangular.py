from pymt import *




a  = MTRectangularWidget(size=(200,200), pos=(200,200))

o = MTRectangularWidget()
a.add_widget(o)

runTouchApp(a)
