import unittest
import pymtcore

__all__ = ['CoreImageTestCase']

class CoreImageTestCase(unittest.TestCase):
    def testImageInvalidFilename(self):
        pymtcore.Image("")
