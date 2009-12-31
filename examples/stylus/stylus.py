
from pymt import *
from OpenGL.GL import *


class PenCanvas(MTScatterPlane):

    def __init__(self, **kwargs):
        super(PenCanvas,self).__init__( **kwargs)
        self.render_batch = []
        self.current_stroke = []


    def append_stroke(self,x,y):
        self.current_stroke.append(int(x))
        self.current_stroke.append(int(y))

    def draw(self):
        set_color(1,1,1)
        for i in self.render_batch:
            drawLine(points=i, width=3)
        if len(self.current_stroke):
           drawLine(points=self.current_stroke, width=3)

    def on_object_down(self, objects, objectID, oid, x, y, angle):
        self.append_stroke(*self.to_local(x, y))

    def on_object_move(self, objects, objectID, oid, x, y, angle):
        self.append_stroke(*self.to_local(x, y))

    def on_object_up(self, objects, objectID, oid, x, y, angle):
        self.append_stroke(*self.to_local(x, y))
        self.render_batch.append(self.current_stroke)
        self.current_stroke = []


w = MTWindow()
w.add_widget(PenCanvas())
runTouchApp()
