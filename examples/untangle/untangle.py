from pymt import *
from graph import *
from pyglet import *

#init our window
w = UIWindow()
w.set_fullscreen()

import time
import pickle
class EventLogger(Widget):
	def __init__(self, parent=None):
		Widget.__init__(self, parent)
		self.touches = {}
	
	def on_touch_down(self, touches, touchID, x,y):
		event = {'type':'down', 'x':x, 'y':y, 't':time.clock() }
		self.touches[touchID] = [event,]
	
	def on_touch_up(self, touches, touchID,x,y):
		event = {'type':'up', 'x':x, 'y':y, 't':time.clock() }
		self.touches[touchID].append(event)

	def on_touch_move(self, touches, touchID, x, y):
		event = {'type':'move', 'x':x, 'y':y, 't':time.clock() }
		self.touches[touchID].append(event)

class TrialLogger():
	def __init__(self, graph):
		self.log = EventLogger()
		graph.parent.add_widget(self.log )
		
		self.graph_start = pickle.dumps(graph)
		
	def save(self,filename):
		self.graph_stop = pickle.dumps(graph)
		f = open(filename,'wb')
		data = {'graph_start': self.graph_start,
			'graph_stop':self.graph_stop,
			'events': self.log.touches}
		pickle.dump(data, f)
		f.close()
		
		
		
		
		

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

root = Widget()
graph = GraphUI(root)
root.add_widget(graph)
log = TrialLogger(graph)

w.add_widget(root)
	
#start the App
runTouchApp()
log.save('data.pkl')