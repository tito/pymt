import unittest
import pymtcore

__all__ = ['VectorTestCase']

class WidgetTestCase(unittest.TestCase):
    def testMethodsAvailability(self):
        self.failUnless(hasattr(pymtcore.MTWidget, 'add_widget'))
        self.failUnless(hasattr(pymtcore.MTWidget, 'remove_widget'))
        self.failUnless(hasattr(pymtcore.MTWidget, 'on_update'))
        self.failUnless(hasattr(pymtcore.MTWidget, 'on_draw'))
        self.failUnless(hasattr(pymtcore.MTWidget, 'draw'))

    def testCreate(self):
        widget = pymtcore.MTWidget()
        self.failUnless(widget is not None)

    def testAppendRemove(self):
        widget1 = pymtcore.MTWidget()
        widget2 = pymtcore.MTWidget()
        self.failUnless(len(widget1.children) == 0)

        widget1.add_widget(widget2)
        self.failUnless(len(widget1.children) == 1)
        self.failUnless(widget2 in widget1.children)

        widget1.remove_widget(widget2)
        self.failUnless(len(widget1.children) == 0)
        self.failUnless(widget2 not in widget1.children)

    def testInvalidRemove(self):
        widget1 = pymtcore.MTWidget()
        widget1.remove_widget(None)


