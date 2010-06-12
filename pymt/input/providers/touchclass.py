from ..touch import Touch
from ..shape import TouchShapeRect

class WM_Pen(Touch):
    '''Touch representing the WM_Pen event. Support pos profile'''
    def depack(self, args):
        self.sx, self.sy = args[0], args[1]
        super(WM_Pen, self).depack(args)

    def __str__(self):
        return '<WMPen id:%d uid:%d pos:%s device:%s>' % (self.id, self.uid, str(self.spos), self.device)

class WM_Touch(Touch):
    '''Touch representing the WM_Touch event. Support pos, shape and size profiles'''
    def depack(self, args):
        self.shape = TouchShapeRect()
        self.sx, self.sy = args[0], args[1]
        self.shape.width = args[2]
        self.shape.height = args[3]
        self.size = self.shape.width * self.shape.height
        self.profile = ('pos', 'shape', 'size')

        super(WM_Touch, self).depack(args)

    def __str__(self):
        return '<WMTouch id:%d uid:%d pos:%s device:%s>' % (self.id, self.uid, str(self.spos), self.device)

class MacTouch(Touch):
    '''Touch representing a contact point on touchpad. Support pos and shape
    profile'''

    def depack(self, args):
        self.shape = TouchShapeRect()
        self.sx, self.sy = args[0], args[1]
        self.shape.width = args[2]
        self.shape.height = args[2]
        self.profile = ('pos', 'shape')
        super(MacTouch, self).depack(args)

    def __str__(self):
        return '<MacTouch id=%d pos=(%f, %f) device=%s>' % (self.id, self.sx, self.sy, self.device)

