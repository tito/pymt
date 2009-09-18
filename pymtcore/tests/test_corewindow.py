import unittest
import pymtcore

__all__ = ['CoreWidgetTestCase']

class CoreWindowTestCase(unittest.TestCase):
    def testSDL(self):
        w = pymtcore.MTCoreWindow()
        print
        w.dump_video_info()
        w.dump_list_modes()

    def testWindowCreation(self):
        w = pymtcore.MTCoreWindow()
        w.size = 320, 240
        self.failUnless(w.setup() == True)
