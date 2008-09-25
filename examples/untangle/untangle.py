from pymt import *
from graph import *
from pyglet import *

#init our window
config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
w = TouchWindow(config)

#init the graph
w.set_fullscreen()
g = Graph(12,displaySize=w.get_size())
touch2vertex = {}


@w.event
def on_draw():
	w.clear()
	g.draw()

@w.event
def on_touch_down(touches, touchID, x,y):
	touchedVertex = g.collideVerts(x,y)
	if touchedVertex: touch2vertex[touchID] = touchedVertex
	
@w.event
def on_touch_up(touches, touchID,x,y):
        if touch2vertex.has_key(touchID):
                del touch2vertex[touchID]

@w.event
def on_touch_move(touches, touchID, x, y):
	if touch2vertex.has_key(touchID):
                touch2vertex[touchID][0] = x
                touch2vertex[touchID][1] = y


	
#start the App

TouchEventLoop().run()
