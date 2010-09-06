from pymt import *

# force background draw for scatter
css_add_sheet('''
scatterwidget {
    draw-background: 1;
}''')

# add a simple scatter
scatter = MTScatterWidget(size=(300, 300), pos=(100, 100), rotation=45)

# add some children in
layout = MTBoxLayout()
layout.add_widget(MTButton(label='A1'))
layout.add_widget(MTButton(label='A2'))
scatter.add_widget(layout)

# now, the scatter is rotated, and the button too.
# it's still possible to click on the button, even
# if they are rotated too
runTouchApp(scatter)
