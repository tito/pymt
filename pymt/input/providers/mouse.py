'''
Mouse: Mouse provider implementation
'''

__all__ = ['MouseTouchProvider']

from collections import deque
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch

class MouseTouch(Touch):
    def depack(self, args):
        self.sx, self.sy = args
        super(MouseTouch, self).depack(args)

class MouseTouchProvider(TouchProvider):
    __handlers__ = {}

    def __init__(self, device, args):
        super(MouseTouchProvider, self).__init__(device, args)
        self.waiting_event  = deque()
        self.window         = None
        self.touches		= {}
        self.counter		= 0
        self.current_drag	= None

    def start(self):
        '''Start the mouse provider'''
        pass

    def stop(self):
        '''Stop the mouse provider'''
        pass

    def find_touch(self, x, y):
        factor = 10. / self.window.width
        for t in self.touches.values():
            if abs(x-t.sx) < factor and abs(y-t.sy) < factor:
                return t
        return False

    def on_mouse_motion(self, x, y, modifiers):
        rx = x / float(self.window.width)
        ry = 1. - y / float(self.window.height)
        if self.current_drag:
            cur = self.current_drag
            cur.move([rx, ry])
            self.waiting_event.append(('move', cur))
        return True


    def on_mouse_press(self, x, y, button, modifiers):
        rx = x / float(self.window.width)
        ry = 1. - y / float(self.window.height)
        newTouch = self.find_touch(rx, ry)
        if newTouch:
            self.current_drag = newTouch
        else:
            self.counter += 1
            id = 'mouse' + str(self.counter)
            self.current_drag = cur = MouseTouch(self.device, id=id, args=[rx, ry])
            if 'shift' in modifiers:
                cur.is_double_tap = True
            self.touches[id] = cur
            self.waiting_event.append(('down', cur))
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        rx = x / float(self.window.width)
        ry = 1. - y / float(self.window.height)
        cur = self.find_touch(rx, ry)
        if button == 'left' and cur and not ('ctrl' in modifiers):
            cur.move([rx, ry])
            del self.touches[cur.id]
            self.waiting_event.append(('up', cur))
        return True

    def update(self, dispatch_fn):
        '''Update the mouse provider (pop event from the queue)'''
        if not self.window:
            from ...base import getWindow
            self.window = getWindow()
            if self.window:
                self.window.push_handlers(
                    on_mouse_move=self.on_mouse_motion,
                    on_mouse_down=self.on_mouse_press,
                    on_mouse_up=self.on_mouse_release
                )
        if not self.window:
            return
        try:
            while True:
                event = self.waiting_event.popleft()
                dispatch_fn(*event)
        except Exception, e:
            pass

# registers
TouchFactory.register('mouse', MouseTouchProvider)
