from pymt import *

win = MTWindow()
scat = MTScatterWidget()
win.add_widget(scat)

s = MTWidget()
c = Camera()
@s.event
def on_draw():
    c.update()
    c.draw()

scat.add_widget(s)
scat.size = (c.width, c.height)
  
runTouchApp()
