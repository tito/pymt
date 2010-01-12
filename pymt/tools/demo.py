import os
from pymt import *

particle_fn = os.path.join(pymt_data_dir, 'particle.png')

class TouchTracer(MTWidget):
    def __init__(self, **kwargs):
        super(TouchTracer, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        color = get_random_color()
        touch.userdata['touchtracer.color'] = color
        touch.userdata['touchtracer.pos'] = list(touch.pos)

    def on_touch_move(self, touch):
        touch.userdata['touchtracer.pos'] += list(touch.pos)

    def draw(self):
        k      = {'anchor_y': 'bottom', 'font_size': 10}
        margin = 4
        set_brush(particle_fn)
        for touch in getCurrentTouches():
            set_color(*touch.userdata['touchtracer.color'])
            paintLine(touch.userdata['touchtracer.pos'], width=5)
            label = 'ID: %s\npos: (%d,%d)\nDevice: %s\nDouble Tap: %s' % (
                    touch.id, touch.pos[0], touch.pos[1],
                    touch.device, str(touch.is_double_tap))

            # draw a little box with margin
            obj = getLabel(label=label, **k)
            pos = Vector(touch.pos) + Vector(0, 10)
            lpos = pos - Vector(obj.width / 2. + margin, margin)
            lsize = Vector(obj.size) + Vector(margin * 2, margin * 2)
            set_color(.2, .2, .4)
            drawRoundedRectangle(pos=(int(lpos.x), int(lpos.y)), size=lsize)
            drawLabel(label=label, pos=pos, **k)


if __name__ == '__main__':
    runTouchApp(TouchTracer())
