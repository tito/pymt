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
        self.failUnless(widget2 in widget1.children)
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
        widget2 = SubWidget().__disown__()
        widget1.add_widget(widget2)
        widget1.on_update()
        self.failUnless(widget2.var == 1)

    def testReferenceCount(self):
        widget = pymtcore.MTWidget()
        widget.print_debug_internal()
        child = pymtcore.MTWidget()
        child.print_debug_internal()
        print "ADD WIDGET"
        widget.add_widget(child)
        child.print_debug_internal()
        child.parent.print_debug_internal()
        print "DERIVATION"
        a = widget
        child.print_debug_internal()
        child.parent.print_debug_internal()
        print "DEL WIDGET"
        del widget
        child.print_debug_internal()
        child.parent.print_debug_internal()
        print "DEL DERIVATION"
        del a
        child.print_debug_internal()
        child.parent.print_debug_internal()

    '''
    def testPerformanceOnupdate(self):
        class SubWidget(pymtcore.MTWidget):
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
        root = pymtcore.MTWidget()
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
        root = pymt.MTWidget()
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
