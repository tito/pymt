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
            def on_move(self, data):
                self.moveto = data
        a = MyWidget()
        a.x = 50
        self.failUnless(a.moveto == (50, 0))
        a.y = 50
        self.failUnless(a.moveto == (50, 50))
        a.pos = (-88, 55)
        self.failUnless(a.moveto == (-88, 55))

    def testOnResize(self):
        class MyWidget(pymtcore.MTCoreWidget):
            def on_resize(self, data):
                self.sizeto = data
        a = MyWidget()
        a.width = 50
        self.failUnless(a.sizeto == (50, 100))
        a.height = 50
        self.failUnless(a.sizeto == (50, 50))
        a.size = (-88, 55)
        self.failUnless(a.sizeto == (-88, 55))

    def testConnect(self):
        global on_move_called, on_move_data
        on_move_called = 0
        on_move_data = None
        def callback_on_move(data):
            global on_move_called, on_move_data
            on_move_called += 1
            on_move_data = data
        a = pymtcore.MTCoreWidget()
        self.failUnless(on_move_called == 0)
        self.failUnless(on_move_data == None)
        a.connect('on_move', callback_on_move)
        self.failUnless(on_move_called == 0)
        self.failUnless(on_move_data == None)
        a.x = 50
        self.failUnless(on_move_called == 1)
        self.failUnless(on_move_data == (50, 0))
        a.y = 50
        self.failUnless(on_move_called == 2)
        self.failUnless(on_move_data == (50, 50))
