import unittest
import pymtcore

__all__ = ['CoreWidgetTestCase']

class CoreWindowTestCase(unittest.TestCase):
    def testWindowCreation(self):
        w = pymtcore.MTCoreWindow()
        #w.dump_video_info()
        #w.dump_list_modes()

    def testWindowSetup320x240(self):
        w = pymtcore.MTCoreWindow()
        w.size = 320, 240
        self.failUnless(w.setup() == True)
