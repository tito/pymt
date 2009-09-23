import unittest
import pymtcore
import os

__all__ = ['CoreImageTestCase']

class CoreImageTestCase(unittest.TestCase):
    def testImagePNG(self):
        filename = os.path.join(os.path.dirname(__file__), 'pngtest.png')
        image = pymtcore.CoreImage(filename)
        self.failUnless(image.pixels is not None)
