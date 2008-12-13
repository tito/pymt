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
		
		
		
		
class GraphUI(Widget):
	def __init__(self, parent=None, size=20):
		Widget.__init__(self, parent)	
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




class HorizontalLayout(RectangularWidget):
	def __init__(self, parent=None, spacing=10, **kargs):
		RectangularWidget.__init__(self, parent, **kargs)
		self.spacing = spacing
		
	def draw(self):
		Widget.draw(self)
		
	def add_widget(self,w):
		Widget.add_widget(self, w)
		self.layout()
		
	def layout(self):
		cur_x = self.x
		for w in self.children:
			try:
				w.x = cur_x
				cur_x += w.width + spacing
			except:
				pass



root = Widget()
graph = GraphUI(root)
log = TrialLogger(graph)




root.add_widget(graph)
w.add_widget(root)
	
#start the App
runTouchApp()
log.save('data.pkl')