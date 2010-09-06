from pymt import *

css_add_sheet('.rect { draw-background: 1; }')

# create a kinetic object
kinetic = MTKinetic()

# add some object on kinetic place
kinetic.add_widget(MTDragable(cls='rect', style={'bg-color': (1, .2, .2, 1)}))
kinetic.add_widget(MTDragable(cls='rect', style={'bg-color': (.2, 1, .2, 1)}))
kinetic.add_widget(MTDragable(cls='rect', style={'bg-color': (.2, .2, 1, 1)}))

# run app with kinetic plane
runTouchApp(kinetic)
