import math

class Vector(object):
    """Represents a 2D vector."""
    __slots__ = ('x', 'y')
    def __init__(self, x = 0.0, y = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector(self.x + val.x, self.y + val.y)

    def __sub__(self,val):
        return Vector(self.x - val.x, self.y - val.y)

    def __iadd__(self, val):
        self.x += val.x
        self.y += val.y
        return self

    def __isub__(self, val):
        self.x -= val.x
        self.y -= val.y
        return self

    def __div__(self, val):
        return Vector(self.x / val, self.y / val)

    def __mul__(self, val):
        return Vector(self.x * val, self.y * val )

    def __idiv__(self, val):
        self.x = self.x / val
        self.y = self.y / val
        return self

    def __imul__(self, val):
        self.x = self.x * val
        self.y = self.y * val
        return self

    def __str__(self):
        return '(%.1f,%.1f)' % (self.x, self.y)

    @staticmethod
    def distanceSqrd(vec1, vec2):
        """Returns the distance between two points squared.
        Marginally faster than Distance()
        """
        return ((vec1.x - vec2.x)**2 + (vec1.y - vec2.y)**2)

    @staticmethod
    def distance(vec1, vec2):
        """Returns the distance between two points"""
        return math.sqrt(self.distanceSqrd(vec1, vec2))

    @staticmethod
    def lengthSqrd(vec):
        """Returns the length of a vector sqaured.
        Faster than Length(), but only  marginally"""
        return vec.x**2 + vec.y**2

    @staticmethod
    def length(vec):
        'Returns the length of a vector'
        return math.sqrt(self.lengthSqrd(vec))

    @staticmethod
    def normalize(vec):
        """Returns a new vector that has the same direction as vec,
        but has a length of one."""
        if vec.x == 0. and vec.y == 0.:
            return Vector(0.,0.)
        return vec / self.length(vec)

    @staticmethod
    def dot(vec1, vec2):
        'Computes the dot product of a and b'
        return vec1.x * vec2.x + vec1.y * vec2.y

