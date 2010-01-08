'''
Show a circle under all touchs
'''

import os
from pymt import MTWidget, set_color, getCurrentTouches, pymt_data_dir, Image

if not 'PYMT_DOC' in os.environ:
    ring_fn = os.path.join(pymt_data_dir, 'ring.png')
    ring_img = Image(ring_fn)
    ring_img.scale = .30
    ring_img.anchor_x = ring_img.width / 2
    ring_img.anchor_y = ring_img.height / 2

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

            # draw touch
            ring_img.pos = touch.pos
            ring_img.draw()

def start(win, ctx):
    ctx.w = TouchRing()
    win.add_widget(ctx.w)

def stop(win, ctx):
    win.remove_widget(ctx.w)
