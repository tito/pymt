
from factory import *

class MTTouch2dCur(MTTouchAbstract):
    def __init__(self, id, args):
        super(MTTouch2dCur, self).__init__(id, args)

    def move(self, args):
        self.dxpos, self.dypos = self.x, self.y
        super(MTTouch2dCur, self).move(args)

    def depack(self, args):
        if len(args) < 5:
            self.x, self.y = args[0:2]
        elif len(args) == 5:
            self.x, self.y, self.X, self.Y, self.m = args[0:5]
        else:
            self.x, self.y, self.X, self.Y, self.m, width, height = args[0:7]
            if self.shape is None:
                self.shape = MTTouchShapeRect()
                self.shape.width = width
                self.shape.height = height
        if self.oxpos is None:
            self.oxpos, self.oypos = self.x, self.y
            self.dxpos, self.dypos = self.x, self.y

MTTouchFactory.register('/tuio/2Dcur', MTTouch2dCur)
