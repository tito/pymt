from pymt import *

l = MTLabel(label='')

class NonGrabObject(MTWidget):
    def __init__(self, **kwargs):
        self.touch = None
        super(NonGrabObject, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        self.touch = touch
        l.label = 'NonGrabObject %s down at (%d, %d)' % (str(touch.id), touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        if self.touch != touch:
            return
        l.label = 'NonGrabObject %s move at (%d, %d)' % (str(touch.id), touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if self.touch != touch:
            return
        l.label = 'NonGrabObject %s up at (%d, %d)' % (str(touch.id), touch.x, touch.y)
        return True

    def draw(self):
        set_color(1, 0, 0)
        drawRectangle(pos=self.pos, size=self.size)

class GrabObject(MTWidget):
    def __init__(self, **kwargs):
        self.touch = None
        super(GrabObject, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        self.touch = touch
        touch.grab(self)
        l.label = 'GrabObject %s down at (%d, %d)' % (str(touch.id), touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        if self.touch != touch:
            return
        l.label = 'GrabObject %s move at (%d, %d)' % (str(touch.id), touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if self.touch != touch:
            return
        l.label = 'GrabObject %s up at (%d, %d)' % (str(touch.id), touch.x, touch.y)
        touch.ungrab(self)
        return True

    def draw(self):
        set_color(0, 0, 1)
        drawRectangle(pos=self.pos, size=self.size)

w = MTWindow()
m = MTRectangularWidget(pos=(200, 100), size=(100, 200))
m.add_widget(GrabObject(pos=(200, 100)))
m.add_widget(NonGrabObject(pos=(200, 200)))
w.add_widget(m)
w.add_widget(l)
runTouchApp()
