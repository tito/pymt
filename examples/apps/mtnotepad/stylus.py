from pymt import *

class Painter(MTWidget):
    def __init__(self, **kwargs):
        super(Painter, self).__init__(**kwargs)
        self.lines = []

    def on_touch_down(self, touch):
        if touch.device == 'wm_pen':
            touch.userdata['line'] = list(touch.pos)
            self.lines.append( touch.userdata['line'] )
            return True

    def on_touch_move(self, touch):
        if touch.device == 'wm_pen':
            touch.userdata['line'].extend(touch.pos)
            return True


    def draw(self):
        for line in self.lines:
            set_color(0,0,0,0.6)
            drawLine(line, width=5)

scatter = MTScatterPlane()
scatter.add_widget(Painter())

runTouchApp(scatter)
