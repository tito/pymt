'''
Show a circle under all touchs
'''

from pymt import MTWidget, set_color, drawCircle, getAvailableTouchs

class TouchRing(MTWidget):
    def __init__(self, **kwargs):
        super(TouchRing, self).__init__(**kwargs)

    def on_update(self):
        self.bring_to_front()

    def draw(self):
        set_color(1, 1, 1, .7)
        for touch in getAvailableTouchs():
            drawCircle(pos=touch.pos, radius=25., linewidth=3.)

def start(win, ctx):
    ctx.w = TouchRing()
    win.add_widget(ctx.w)

def stop(win, ctx):
    win.remove_widget(ctx.w)
