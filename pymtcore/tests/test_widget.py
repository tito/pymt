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

    def testInheritance(self):
        class SubWidget(pymtcore.MTWidget):
            def __init__(self):
                super(SubWidget, self).__init__()
                self.var = 0
            def on_update(self):
                self.var += 1
                super(SubWidget, self).on_update()
        widget1 = pymtcore.MTWidget()
        widget2 = SubWidget()
        widget1.add_widget(widget2)
        widget1.on_update()
        self.failUnless(widget2.var == 1)

    '''
    def testPerformanceOnupdate(self):
        class SubWidget(pymtcore.MTWidget):
            def __init__(self):
                super(SubWidget, self).__init__()
                self.var = 0
            def on_update(self):
                super(SubWidget, self).on_update()

        print 'Preparing...'
        root = pymtcore.MTWidget()
        for x in xrange(100):
            wid = SubWidget().__disown__()
            for y in xrange(1000):
                wid.add_widget(SubWidget().__disown__())
            root.add_widget(wid)

        import sys, time
        starttime = time.time()
        print 'Start update on 100*1000 widgets'
        for x in xrange(20):
            sys.stderr.write('.')
            root.on_update()
        endtime = time.time()
        print 'Update finished', endtime - starttime

        # real pymt
        sys.argv = ['']
        import pymt

        print 'Preparing...'
        root = pymt.MTWidget()
        for x in xrange(100):
            wid = pymt.MTDragable()
            for y in xrange(1000):
                wid.add_widget(pymt.MTButton())
            root.add_widget(wid)

        import sys, time
        starttime = time.time()
        print 'Start update on 100*1000 widgets'
        for x in xrange(20):
            sys.stderr.write('.')
            root.on_update()
        endtime = time.time()
        print 'Update finished', endtime - starttime
    '''
