from factory import *

class MTTouch2dObj(MTTouchAbstract):
    def __init__(self, id, args):
        super(MTTouch2dObj, self).__init__(id, args)

    def move(self, args):
        self.dxpos, self.dypos = self.x, self.y
        super(MTTouch2dObj, self).move(args)

    def depack(self, args):
        if len(args) < 5:
            self.x, self.y = args[0:2]
            self.profile = 'xy'
        elif len(args) == 9:
            self.id, self.x, self.y, self.a, self.X, self.Y, self.A, self.m, self.r = args[0:9]
            self.profile = 'ixyaXYAmr'
        else:
            self.id, self.x, self.y, self.a, self.X, self.Y, self.A, self.m, self.r, width, height = args[0:11]
            self.profile = 'ixyaXYAmrh'
            if self.shape is None:
                self.shape = MTTouchShapeRect()
                self.shape.width = width
                self.shape.height = height

MTTouchFactory.register('/tuio/2Dobj', MTTouch2dObj)
