
from pymt import *
from pyglet.graphics import *
from pyglet.gl import *



class PenCanvas(MTScatterPlane):

    def __init__(self, **kwargs):
        super(PenCanvas,self).__init__( **kwargs)
        self.render_batch = Batch()
        self.current_stroke = []
        

    def append_stroke(self,x,y):         
        self.current_stroke.append(int(x))
        self.current_stroke.append(int(y))

    def draw(self):
        glLineWidth(3)
        self.render_batch.draw()
        if len(self.current_stroke):
            draw(len(self.current_stroke)/2, GL_LINES, ('v2i', self.current_stroke))

                
    def on_object_down(self, objects, objectID, oid, x, y, angle):
        self.append_stroke(*self.to_local(x,y))

    def on_object_move(self, objects, objectID, oid, x, y, angle):
        self.append_stroke(*self.to_local(x,y))
        self.append_stroke(*self.to_local(x,y))

    def on_object_up(self, objects, objectID, oid, x, y, angle):
        self.append_stroke(*self.to_local(x,y))
        vertex_list = self.render_batch.add(len(self.current_stroke)/2, GL_LINES, None, ('v2i', self.current_stroke))
        self.current_stroke = []
            

w = MTWindow()
w.add_widget(PenCanvas())
runTouchApp()
