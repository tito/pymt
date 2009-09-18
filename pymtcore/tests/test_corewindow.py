import unittest
import pymtcore

__all__ = ['CoreWidgetTestCase']

class CoreWindowTestCase(unittest.TestCase):
    def testSDL(self):
        w = pymtcore.MTCoreWindow()
        w.dump_video_info()
        w.dump_list_modes()

    def testWindowCreation(self):
        w = pymtcore.MTCoreWindow()
        self.failUnless(w.setup(320, 200, False) == True)
