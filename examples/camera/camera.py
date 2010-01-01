from pymt import *

scat = MTScatterWidget()

s = MTWidget()
c = Camera()
@s.event
def on_draw():
    c.update()
    c.draw()

scat.add_widget(s)
scat.size = (c.width, c.height)

runTouchApp(scat)
