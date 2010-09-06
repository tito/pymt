from pymt import *

w = MTWidget()

y = 0
for halign in ('left', 'center', 'right'):
    y += 100
    x = 100
    for valign in ('top', 'center', 'bottom'):
        m = MTButton(label='%s:%s' % (halign, valign),
                     pos=(x, y), size=(150, 30),
                     anchor_x=halign, anchor_y=valign)
        x += 200
        w.add_widget(m)

runTouchApp(w)
