from pymt import *

# force background draw for scatter
css_add_sheet('''
scatterwidget {
    draw-background: 1;
}''')

# add a simple scatter
scatter = MTScatterWidget(size=(300, 300))

runTouchApp(scatter)
