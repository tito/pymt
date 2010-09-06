from pymt import *

class MyWidget(MTWidget):
	def __init__(self, **kwargs):
		super(MyWidget, self).__init__(**kwargs)

	def on_draw(self):
		for w in self.children:
			w.dispatch_event('on_draw')
		c = self.children[-1].children[-1]
		cwinpos = c.to_window(*c.pos)
		set_color(0, 1, 0, 1)
		drawLine((0, 0, cwinpos[0], cwinpos[1]))

		set_color(0, 0, 1, 1)
		drawLine((0, 0, c.x, c.y))

w = MTWindow()
root = MyWidget()
s1 = MTScatterWidget(style={'bg-color': (1, 0, 0, 1)}, size=(200, 200))
s2 = MTScatterWidget(style={'bg-color': (1, 1, 0, 1)})
s1.add_widget(s2)
root.add_widget(s1)
w.add_widget(root)
print ''
print 'Blue line represent the (0, 0) -> scatter.pos (invalid in this case)'
print 'Green line represent the (0, 0) -> scatter position for window (valid)'
print ''
runTouchApp()
