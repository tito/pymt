from __future__ import with_statement
from pymt import *


class HVMatrixButton(MTButton):
    def __init__(self, **kwargs):
        super(HVMatrixButton, self).__init__(**kwargs)

    def on_press(self, *largs):
        self.parent.children_active.append(self)

    def on_release(self, *largs):
        if self in self.parent.children_active:
            self.parent.children_active.remove(self)

    def draw(self):
        if self._state[0] == 'down':
            set_color(*self.style.get('color-down'))
        else:
            set_color(*self.style.get('bg-color'))
        drawRoundedRectangle(self.pos, self.size)

class HVMatrix(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('matrix_size', (3,3))
        kwargs.setdefault('spacing', 5)
        super(HVMatrix, self).__init__(**kwargs)
        self.matrix_size = kwargs.get('matrix_size')
        self.spacing = kwargs.get('spacing')
        self.dl = GlDisplayList()
        self.children_active = []

    def add_widget(self, widget, do_layout=True):
        if len(self.children) >= self.matrix_size[0] * self.matrix_size[1]:
            raise Exception('Too much children in HVMatrix. Increase your matrix_size!')
        if not isinstance(widget, HVMatrixButton):
            raise Exception('Only HVMatrixButton instance are allowed.')
        super(HVMatrix, self).add_widget(widget)
        if do_layout:
            self.layout()

    def layout(self):
        i = 0
        mx, my = self.matrix_size
        spacing = self.spacing
        sx = spacing + (self.width - spacing * (mx + 1)) / mx
        sy = spacing + (self.height - spacing * (my + 1)) / my
        for x in range(my):
            for y in range(my):
                if i >= len(self.children):
                    break
                c = self.children[i]
                c.pos = ((x * (sx + spacing) + spacing, y * (sy + spacing) + spacing))
                c.size = (sx, sy)
                i = i + 1
        self.dl.clear()

    def on_draw(self):
        if not self.dl.is_compiled():
            with self.dl:
                for w in self.children:
                    w.dispatch_event('on_draw')
        self.draw()

    def on_resize(self, w, h):
        self.layout()

    def draw(self):
        self.dl.draw()
        for w in self.children_active:
            w.dispatch_event('on_draw')


if __name__ == '__main__':
    w = MTWindow()
    m = HVMatrix(matrix_size=(20, 20), size=w.size)

    for i in range(20*20):
        b = HVMatrixButton(color=(.8,.8,.8,.5), label='B%d'%i, bold=False)
        m.add_widget(b, do_layout=False)
    m.layout()

    w.add_widget(m)
    runTouchApp()

