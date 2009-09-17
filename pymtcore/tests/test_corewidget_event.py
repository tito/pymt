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
