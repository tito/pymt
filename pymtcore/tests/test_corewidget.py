import unittest
import pymtcore

__all__ = ['CoreWidgetTestCase']

class CoreWidgetTestCase(unittest.TestCase):
    def testMethodsAvailability(self):
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'add_widget'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'remove_widget'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'draw'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'on_draw'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'on_touch_down'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'on_touch_move'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'on_touch_up'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'on_update'))
        self.failUnless(hasattr(pymtcore.MTCoreWidget, 'remove_widget'))

    def testCreate(self):
        widget = pymtcore.MTCoreWidget()
        self.failUnless(widget is not None)

    def testChildrenVectorIn(self):
        widget1 = pymtcore.MTCoreWidget()
        widget2 = pymtcore.MTCoreWidget()
        widget1.add_widget(widget2)
        self.failUnless(widget2 in widget1.children)

    def testChildrenVector0(self):
        widget1 = pymtcore.MTCoreWidget()
        widget2 = pymtcore.MTCoreWidget()
        widget1.add_widget(widget2)
        self.failUnless(widget1.children[0] == widget2)

    def testAppendRemove(self):
        widget1 = pymtcore.MTCoreWidget()
        widget2 = pymtcore.MTCoreWidget()
        self.failUnless(widget2 not in widget1.children)
        self.failUnless(len(widget1.children) == 0)

        widget1.add_widget(widget2)
        self.failUnless(len(widget1.children) == 1)
        self.failUnless(widget2 in widget1.children)

        widget1.remove_widget(widget2)
        self.failUnless(len(widget1.children) == 0)
        self.failUnless(widget2 not in widget1.children)

    def testInvalidRemove(self):
        widget1 = pymtcore.MTCoreWidget()
        widget1.remove_widget(None)

    def testInheritance(self):
        class SubWidget(pymtcore.MTCoreWidget):
            def __init__(self):
                super(SubWidget, self).__init__()
                self.var = 0
            def on_update(self):
                self.var += 1
                super(SubWidget, self).on_update()
        widget1 = pymtcore.MTCoreWidget()
        widget2 = SubWidget().__disown__()
        widget1.add_widget(widget2)
        widget1.on_update()
        self.failUnless(widget2.var == 1)

    def testReferenceCount(self):
        widget = pymtcore.MTCoreWidget()
        child = pymtcore.MTCoreWidget()
        self.failUnless(widget.get_ref_count() == 1)
        self.failUnless(child.get_ref_count() == 1)
        widget.add_widget(child)
        self.failUnless(widget.get_ref_count() == 2)
        self.failUnless(child.get_ref_count() == 2)

        # we stay in python, and swig is still used
        # normally, reference counter don't move.
        a = widget
        self.failUnless(a.get_ref_count() == 2)
        self.failUnless(child.get_ref_count() == 2)

        # we remove one widget, but a still exist.
        del widget
        self.failUnless(a.get_ref_count() == 2)
        self.failUnless(child.get_ref_count() == 2)

        # no more reference on initial widget
        # the child is now orphan
        del a
        self.failUnless(child.get_ref_count() == 1)
        self.failUnless(child.parent == None)

    def testToLocal(self):
        widget = pymtcore.MTCoreWidget()
        res = widget.to_local(1, 2)
        self.failUnless(res == (1, 2))

    def testSpam(self):
        pymtcore.spam(1, 2)

    '''
    def testPerformanceOnupdate(self):
        class SubWidget(pymtcore.MTCoreWidget):
            def __init__(self):
                super(SubWidget, self).__init__()
                self.var = 0
            def on_update(self):
                super(SubWidget, self).on_update()

        import sys, time
        sys.argv = ['']
        import pymt


        print ''
        print '============================================================'

        starttime = time.time()
        print '[C++] Creating widgets structure (100 with 1000 childrens each)...'
        root = pymtcore.MTCoreWidget()
        for x in xrange(100):
            wid = SubWidget()
            for y in xrange(1000):
                wid.add_widget(SubWidget())
            root.add_widget(wid)
        endtime = time.time()
        print '[C++] Creation done in', endtime - starttime

        starttime = time.time()
        print '[C++] Calling root.on_update()'
        for x in xrange(20):
            sys.stderr.write('.')
            root.on_update()
        endtime = time.time()
        print
        print '[C++] Calling done in', endtime - starttime

        starttime = time.time()
        print '[PyMT] Creating widgets structure (100 with 1000 childrens each)...'
        root = pymt.MTCoreWidget()
        for x in xrange(100):
            wid = pymt.MTDragable()
            for y in xrange(1000):
                wid.add_widget(pymt.MTButton())
            root.add_widget(wid)
        endtime = time.time()
        print '[PyMT] Creation done in', endtime - starttime

        import sys, time
        starttime = time.time()
        print '[PyMT] Calling root.on_update()'
        for x in xrange(20):
            sys.stderr.write('.')
            root.on_update()
        endtime = time.time()
        print
        print '[PyMT] Calling done in', endtime - starttime
        print '============================================================'
    '''
