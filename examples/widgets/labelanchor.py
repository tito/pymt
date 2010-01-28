from pymt import *

layout = MTGridLayout(cols=3)

size = (200, 200)
text = 'Hello World\nAnchor X: %s\nAnchor Y: %s'
style = {'bg-color': (0, .2, 0, 1), 'draw-background': 1}

for anchor_x in ('left', 'center', 'right'):
    for anchor_y in ('top', 'middle', 'bottom'):
        label = MTLabel(label=text % (anchor_x, anchor_y), size=size,
                anchor_x=anchor_x, anchor_y=anchor_y,
                halign=anchor_x, valign=anchor_y,
                style=style)
        layout.add_widget(label)

runTouchApp(layout)
