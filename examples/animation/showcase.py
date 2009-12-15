import os
from pymt import *
from OpenGL.GL import *

image_fn = os.path.join(os.path.dirname(__file__), 'icons', 'greeny.png')

class MTGraph(MTKineticItem):
    def __init__(self, **kwargs):
        super(MTGraph, self).__init__(**kwargs)
        # precision of the graph in pixels
        self.precision = 50
        # margin between graph in pixels
        self.margin = 50
        # alpha functions
        self.funcname = kwargs.get('funcname')
        self.func = getattr(AnimationAlpha, self.funcname)
        # get all points for curve with the selected alpha function
        self.points = []
        for x in xrange(0, self.precision):
            progress = x / float(self.precision)
            self.points += [progress, self.func(progress)]
        # add the last one
        self.points += [1., 1.]

        # states
        self.selected = False
        self.progress = 0


    def draw(self):
        # background
        if self.selected:
            set_color(0, 0.1, 0)
        else:
            set_color(0, 0, 0)
        drawRectangle(pos=self.pos, size=self.size)
        drawLabel(label=str(self.funcname), font_size=20,
            pos=(self.x + self.width / 2., self.y + 10),
            anchor_x='center', anchor_y='bottom')

        with gx_matrix:

            m = self.margin
            w, h = self.size

            # axes
            glTranslatef(self.x + m, self.y + m, 0)
            set_color(1, 1, 1)
            drawLine((0, 0, w - m * 2, 0))
            drawLine((0, 0, 0, h - m * 2))

            # curve
            set_color(.2, .2, 1)
            glScalef(w - m * 2, h - m * 2, 0)
            drawLine(self.points, width=2)

            set_color(1, 0, 0, .6)
            drawCircle(pos=(self.progress, self.func(self.progress)),
                       radius=0.05)
            drawLine((self.progress, 0, self.progress, 1.))



class Showcase(MTWidget):
    def __init__(self, **kwargs):
        super(Showcase, self).__init__(**kwargs)
        self.list = MTKineticList(size=(300, 300),
                        deletable=False, searchable=False,
                        title='Easing functions',
                        padding_x=0, friction=1)

        self.add_widget(self.list)

        # enumerate easing function in AnimationAlpha
        for w in dir(AnimationAlpha):
            if w.startswith('_'):
                continue
            graph = MTGraph(size=(300, 300), funcname=w)
            graph.connect('on_press', curry(self.on_graph_press, graph))
            self.list.add_widget(graph)

        # create animation object
        self.object = MTContainer(Image(image_fn), pos=(400, 400))
        self.add_widget(self.object)

        # states
        self.current = None
        self.animation = None

    def on_update(self):
        w = self.get_parent_window()
        self.list.height = w.height

        # copy progression
        if self.current and self.animation:
            if self.object in self.animation.children:
                base = self.animation.children[self.object]
                self.current.progress = max(0., min(
                    base.frame_pointer / base.duration, 1.))

    def on_graph_press(self, graph, *largs):
        if self.current is not None:
            self.current.selected = False
        self.current = graph
        self.current.selected = True

        # create animation
        w = self.get_parent_window()
        f = graph.funcname
        wi = self.list.width + (w.width - self.list.width) / 2.
        h = self.object.height

        self.animation = Animation(d=1.5, f=f, pos=(wi, w.height - h * 2))

        # reset pos
        self.object.pos = (wi, h)

        # start anim
        self.object.do(self.animation)


if __name__ == '__main__':
    runTouchApp(Showcase())
