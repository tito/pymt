from urllib2 import urlopen
from pymt import *


class MovidGUIDrawer(MTWidget):
    '''
    This PyMT module allows adding an overlay to the current application in which
    a movid module's gui is drawn.
    This can be used e.g. for movid's calibration module in such a way that you don't
    have to leave your current PyMT application in order to recalibrate your
    touch screen.
    '''
    # FIXME make configurable in config
    def __init__(self, url="http://127.0.0.1:7500/pipeline/", objectname="calib", **kwargs):
        self.url = url
        self.objectname = objectname
        super(MovidGUIDrawer, self).__init__(**kwargs)
        self.pos = (0, 0)
        self.size = getWindow().size
        self.vw = 1000
        self.vh = 1000
        self.instructions = []
        # XXX should depend on movid's update rate
        getClock().schedule_interval(self.fetch_drawing_instructions, 1.)

    def transform_coords(self, x, y):
        ww, wh = getWindow().size
        x = float(x) / self.vw * ww
        # Movid's origin is upper left corner, PyMT is bottom left.
        y = -((float(y) / self.vh * wh) - wh)
        return x, y

    def fetch_drawing_instructions(self, dt):
        if self.parent is not None:
            fd = urlopen(self.url + "gui?objectname=" + self.objectname)
            self.instructions = [s.split() for s in fd.read().split("\n")]

    def draw(self):
        set_color(0, 0, 0, 0.2)
        drawRectangle(self.pos, self.size)
        for ins in self.instructions:
            if not ins:
                continue
            cmd = ins[0]
            p = ins[1:]
            if cmd == "viewport":
                self.vw, self.vh = float(p[0]), float(p[1])
            elif cmd == "circle":
                x, y = self.transform_coords(p[0], p[1])
                r = float(p[2])
                drawCircle((x, y), r)
            elif cmd == "color":
                set_color(*[int(c)/255. for c in p])
            elif cmd == "line":
                x1, y1 = self.transform_coords(p[0], p[1])
                x2, y2 = self.transform_coords(p[2], p[3])
                drawLine((x1, y1, x2, y2))
            else:
                print cmd, "NOT YET SUPPORTED!"
                print cmd, p

    def on_touch_down(self, touch):
        # Don't pass touches to other widgets while movid gui is active.
        # XXX No gui feedback implemented in movid yet, so just pass
        pass


def start(win, ctx):
    drawer = MovidGUIDrawer()
    def _on_keyboard_handler(key, scancode, unicode):
        if key == 290: # F9
            if drawer in win.children:
                win.remove_widget(drawer)
            else:
                win.add_widget(drawer)

    win.push_handlers(on_keyboard=_on_keyboard_handler)


def stop(win, ctx):
    # win.remove_handlers(on_keyboard=_on_keyboard_handler)
    pass


if __name__ == "__main__":
    gui = MovidGUIDrawer()
    runTouchApp(gui)

