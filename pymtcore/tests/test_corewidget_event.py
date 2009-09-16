import unittest
import pymtcore

__all__ = ['CoreWidgetEventTestCase']

class CoreWidgetEventTestCase(unittest.TestCase):
    def testOnTouchDown(self):
        class MyWidget(MTCoreWidget):
            def on_touch_down(self, touch):
                print touch
        class Touch:
            pass
        a = MyWidget()
        touch = Touch()
        a.on_touch_down(touch)
