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
                print 'plop'
                self.moveto = x, y
        a = MyWidget()
        a.x = 50
        self.failUnless(a.moveto == (50, 0))
        a.y = 50
        self.failUnless(a.moveto == (50, 50))
        #import time
        #print "now"
        #time.sleep(2)
        a._set_pos((-88, 55))
        a.pos = (-88, 55)
        self.failUnless(a.moveto == (-88, 55))
