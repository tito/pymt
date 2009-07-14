import unittest
from pymt import Vector

__all__ = ['VectorTestCase']

class VectorTestCase(unittest.TestCase):
    def setUp(self):
        self.v = Vector(10, 10)

    def testX(self):
        self.failUnless(self.v.x == 10)

    def testY(self):
        self.failUnless(self.v.y == 10)

    def testAdd(self):
        a = Vector(1, 1)
        b = Vector(2, 2)
        c = a + b
        self.failUnless(c.x == 3)
        self.failUnless(c.y == 3)

    def testCmp(self):
        a = Vector(1, 1)
        b = Vector(2, 2)
        self.failUnless(a != b)
        a = Vector(2, 2)
        self.failUnless(a == b)

