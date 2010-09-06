from pymt import *

css_add_sheet('rectangularwidget { draw-background: 1; }')

# create our root rectangular widget
root = MTRectangularWidget()

# create a rectangular widget, outside the first one
child  = MTRectangularWidget(size=(200,200), pos=(200,200))

root.add_widget(child)

runTouchApp(root)
