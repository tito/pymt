from pymt import *

s = MTWidget()
c = Camera()
@s.event
def on_draw():
    c.update()
    c.draw()
runTouchApp(s)
