from pymt import *

w = MTLabel(label="Hello PyMT Designer!")

def draw_touches():
    for t in getAvailableTouchs():
        set_color(1,0,0)
        drawCircle(pos=t.pos, radius=50)

w.push_handlers(on_draw=draw_touches)

runTouchApp(w)
