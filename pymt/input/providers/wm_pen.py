'''
WM_PEN: Support of WM_PEN message (Window platform)
'''

__all__ = ['WM_PenProvider']

import os
from ctypes import *
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ...utils import curry

if 'PYMT_DOC' not in os.environ:
    from ...base import getWindow

MI_WP_SIGNATURE      = 0xFF515700
SIGNATURE_MASK       = 0xFFFFFF00
PEN_EVENT_TOUCH_MASK = 0x80
WM_MOUSEMOVE         = 512
WM_LBUTTONDOWN       = 513
WM_LBUTTONUP         = 514

class WM_PenProvider(TouchProvider):

    def mouse_msg_handler(self, win, msg, wparam, lParam):

        info = windll.user32.GetMessageExtraInfo()
        if (info & SIGNATURE_MASK) == MI_WP_SIGNATURE:
            if not info & PEN_EVENT_TOUCH_MASK:
                win.last_mouse_event_device = 'pen'
        else:
            win.last_mouse_event_device = 'mouse'

        self.old_mouse_handler(msg, wparam, lParam)


    def pen_callback_move(self, win, type, x, y,dx,dy, mod=None, button=None):
        return self.pen_callback(win,type, x, y, mod, button)


    def pen_callback(self, win, type, x, y, mod=None, button=None):
        #print 'event-device', win.last_mouse_event_device

        if win.last_mouse_event_device == 'pen':
            x = float(x)/win.width
            y = float(y)/win.height
            win.pen_events.append( (type,x,y) )
            return True


    def start(self):
        self.uid = 0

        win = getWindow()
        win.pen = None
        win.pen_events = []

        #pen and touch events come in as mouse events also
        self.old_mouse_handler = win._event_handlers[WM_MOUSEMOVE]
        win._event_handlers[WM_MOUSEMOVE] = curry(self.mouse_msg_handler, win)

        win.push_handlers(on_mouse_press   = curry(self.pen_callback, win,'down' ) )
        win.push_handlers(on_mouse_drag    = curry(self.pen_callback_move, win,'move') )
        win.push_handlers(on_mouse_release = curry(self.pen_callback, win,'up' ) )


    def update(self, dispatch_fn):
        win = getWindow()
        skipped = []
        win_x, win_y = win.get_location()

        #dispatch pen events
        while len(win.pen_events):
            type,x,y = win.pen_events.pop(0)

            if  type == 'down':
                self.uid += 1
                win.pen = WM_Pen(self.device,self.uid, [x,y])

            if  win.pen:
                win.pen.move([x,y])
                dispatch_fn(type, win.pen )

            if type == 'up':
                win.pen = None


    def stop(self):
        pass

class WM_Pen(Touch):

    def depack(self, args):
        self.sx, self.sy = args[0], args[1]
        super(WM_Pen, self).depack(args)

    def __str__(self):
        return "WMpen, id:%d, pos:(%f,%f, device:%s )" % (self.id, self.sx, self.sy, self.device)

TouchFactory.register('WM_PEN', WM_PenProvider)
