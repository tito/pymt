'''
Show a circle under all touchs
'''

from pymt import MTWidget, set_color, drawCircle, getCurrentTouches

class TouchRing(MTWidget):
    def __init__(self, **kwargs):
        super(TouchRing, self).__init__(**kwargs)

    def on_update(self):
        self.bring_to_front()

    def draw(self):
        for touch in getCurrentTouches():
            if 'kinetic' in touch.profile:
                set_color(1, 1, 1, .2)
            else:
                set_color(1, 1, 1, .7)
            drawCircle(pos=touch.pos, radius=25., linewidth=3.)

def start(win, ctx):
    ctx.w = TouchRing()
    win.add_widget(ctx.w)

def stop(win, ctx):
    win.remove_widget(ctx.w)
