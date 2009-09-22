import unittest
import pymtcore
import os

__all__ = ['PerfComparaisonTestCase']

if os.getenv('DOPERF') is not None:

    class PerfComparaisonTestCase(unittest.TestCase):
        def testPerformanceOnupdate(self):
            class SubWidget(pymtcore.MTCoreWidget):
                def __init__(self):
                    super(SubWidget, self).__init__()
                    self.var = 0
                def on_update(self, *largs):
                    super(SubWidget, self).on_update(*largs)

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
                root.on_update([])
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
