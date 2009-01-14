from pymt import *
from graph import *
from pyglet import *

#init our window
w = MTWindow()
w.set_fullscreen()

import time
import pickle


"""
I use the EventLogger and TrialLogger classes to record all the touch input, so that I can visuakize/analyze the user interacitons for some user studies I am working on.
They have absolutly nothing to do with the Graph untabgle game, i case anyone is trying to read this to learn pymt.
"""
class EventLogger(MTWidget):
	def __init__(self, parent=None):
		MTWidget.__init__(self, parent)
		self.touches = {}
		self.enabled = False
	
	def start(self):
		self.enabled = True
		
	def stop(self):
		self.enabled = False
		
	def clear(self):
		self.touches = {}
	
	def on_touch_down(self, touches, touchID, x,y):
		if self.enabled:
			event = {'type':'down', 'id':touchID, 'x':x, 'y':y, 't':time.clock() }
			self.touches[touchID] = [event,]
	
	def on_touch_up(self, touches, touchID,x,y):
		if self.enabled:
			event = {'type':'up', 'id':touchID, 'x':x, 'y':y, 't':time.clock() }
			self.touches[touchID].append(event)

	def on_touch_move(self, touches, touchID, x, y):
		if self.enabled:
			event = {'type':'move', 'id':touchID, 'x':x, 'y':y, 't':time.clock() }
			self.touches[touchID].append(event)


class TrialLogger(EventLogger):
	def __init__(self, widget):
		EventLogger.__init__(self)
		self.widget = widget
		widget.parent.add_widget(self)
		self.widget_start = None
		
	
	def start(self):
		self.widget_start = pickle.dumps(self.widget)
		self.enabled = True
		
	
		
	def save(self,filename):
		self.stop()
		self.widget_stop = pickle.dumps(self.widget)
		
		f = open(filename,'wb')
		data = {'graph_start': self.widget_start,
			'widget_stop':self.widget_stop,
			'touch_events': self.touches}
		pickle.dump(data, f)
		f.close()
		
		
		
		
class GraphUI(MTWidget):
	def __init__(self, parent=None, size=20):
		MTWidget.__init__(self, parent)	
		self.g = Graph(size,displaySize=w.get_size())
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




root = MTWidget()
graph = GraphUI(root)
#log = TrialLogger(graph)
root.add_widget(graph)
w.add_widget(root)
	
#start the App
runTouchApp()
#log.save('data.pkl')
