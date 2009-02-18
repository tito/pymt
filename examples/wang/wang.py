# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Wang game !'

from pymt import *

class Bat(MTWidget):
	def __init__(self, va, vb, **kwargs):
		self.va = va
		self.vb = vb
		super(Bat, self).__init__(**kwargs)

	def draw(self):
		glColor3f(1, 1, 1)
		drawLine([self.va.x, self.va.y, self.vb.x, self.vb.y])

class Wang(MTWidget):
	def __init__(self, **kwargs):
		kwargs.setdefault('mindist', 200)
		super(Wang, self).__init__(**kwargs)
		self.touchs = {}
		self.bats = []
		self.mindist = kwargs.get('mindist')

	def draw(self):
		for b in self.bats:
			b.draw()

	def update_bat(self):
		self.bats = []
		if len(self.touchs) < 2:
			return
		keys = self.touchs.keys()
		for ka in keys:
			va = self.touchs[ka]
			for kb in keys[1:]:
				vb = self.touchs[kb]
				if Vector.distance(va, vb) < self.mindist:
					self.bats.append(Bat(va, vb))

	def on_touch_down(self, touches, touchID, x, y):
		self.touchs[touchID] = Vector(x, y)
		self.update_bat()

	def on_touch_move(self, touches, touchID, x, y):
		if self.touchs.has_key(touchID):
			self.touchs[touchID] = Vector(x, y)
			self.update_bat()
			return True

	def on_touch_up(self, touches, touchID, x, y):
		if self.touchs.has_key(touchID):
			del self.touchs[touchID]
			self.update_bat()
			return True


if __name__ == '__main__':
    w = MTWindow()
    w.add_widget(Wang(mindist=200))

    runTouchApp()
