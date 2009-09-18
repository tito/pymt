import unittest
import pymtcore

__all__ = ['CoreWidgetEventTestCase']

class CoreWidgetEventTestCase(unittest.TestCase):
    def testOnTouchDown(self):
        class MyWidget(pymtcore.MTCoreWidget):
            def on_touch_down(self, touch):
                touch.ok = 1
        class Touch:
            pass
        a = MyWidget()
        touch = Touch()
        a.on_touch_down(touch)
        self.failUnless(touch.ok == 1)

    def testOnMove(self):
        class MyWidget(pymtcore.MTCoreWidget):
            def on_move(self, x, y):
                self.moveto = x, y
        a = MyWidget()
        a.x = 50
        self.failUnless(a.moveto == (50, 0))
        a.y = 50
        self.failUnless(a.moveto == (50, 50))
        a.pos = (-88, 55)
        self.failUnless(a.moveto == (-88, 55))

    def testOnResize(self):
        class MyWidget(pymtcore.MTCoreWidget):
            def on_resize(self, x, y):
                self.sizeto = x, y
        a = MyWidget()
        a.width = 50
        self.failUnless(a.sizeto == (50, 100))
        a.height = 50
        self.failUnless(a.sizeto == (50, 50))
        a.size = (-88, 55)
        self.failUnless(a.sizeto == (-88, 55))
