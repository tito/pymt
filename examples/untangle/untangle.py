from pymt import *
from graph import *
from pyglet import *

#init our window
w = UIWindow()
w.set_fullscreen()


class GraphUI(Widget):

	def __init__(self, parent=None):
		Widget.__init__(self, parent)	
		self.g = Graph(24,displaySize=w.get_size())
		self.touch2vertex = {}
		
	def draw(self):
		self.g.draw()

	def on_touch_down(self, touches, touchID, x,y):
		touchedVertex = self.g.collideVerts(x,y)
		if touchedVertex: self.touch2vertex[touchID] = touchedVertex
	
	def on_touch_up(self, touches, touchID,x,y):
	        if self.touch2vertex.has_key(touchID):
	                del self.touch2vertex[touchID]

	def on_touch_move(self, touches, touchID, x, y):
		if self.touch2vertex.has_key(touchID):
	                self.touch2vertex[touchID][0] = x
	                self.touch2vertex[touchID][1] = y


w.add_widget(GraphUI())
	
#start the App
runTouchApp()
