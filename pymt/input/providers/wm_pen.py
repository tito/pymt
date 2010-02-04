'''
WM_PEN: Support of WM_PEN message (Window platform)
'''

__all__ = ('WM_PenProvider', 'WM_Pen')

import os
from ..touch import Touch

class WM_Pen(Touch):
    '''Touch representing the WM_Pen event. Support pos profile'''
    def depack(self, args):
        self.sx, self.sy = args[0], args[1]
        super(WM_Pen, self).depack(args)

    def __str__(self):
        return '<WMPen id:%d uid:%d pos:%s device:%s>' % (self.id, self.uid, str(self.spos), self.device)

if 'PYMT_DOC' in os.environ:
    # documentation hack
    WM_PenProvider = None

else:
    from ...base import getWindow
    from ctypes import *
    from ..provider import TouchProvider
    from ..factory import TouchFactory

    WNDPROC = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)
    GWL_WNDPROC            = -4
    PEN_OR_TOUCH_SIGNATURE = 0xFF515700
    PEN_OR_TOUCH_MASK      = 0xFFFFFF00
    PEN_EVENT_TOUCH_MASK   = 0x80
    WM_MOUSEMOVE           = 512
    WM_LBUTTONDOWN         = 513
    WM_LBUTTONUP           = 514


    class RECT(Structure):
        _fields_ = [
        ('left',   wintypes.ULONG ),
        ('top',    wintypes.ULONG ),
        ('right',  wintypes.ULONG ),
        ('bottom', wintypes.ULONG )
        ]

        x = property(lambda self: self.left)
        y = property(lambda self: self.top)
        w = property(lambda self: self.right-self.left)
        h = property(lambda self: self.bottom-self.top)
    win_rect = RECT()


    class WM_PenProvider(TouchProvider):

        def _is_pen_message(self, msg):
            info = windll.user32.GetMessageExtraInfo()
            if (info & PEN_OR_TOUCH_MASK) == PEN_OR_TOUCH_SIGNATURE: # its a touch or a pen
                if not info & PEN_EVENT_TOUCH_MASK:
                    return True

        def _pen_handler(self, msg, wParam, lParam):
            windll.user32.GetClientRect(self.hwnd, byref(win_rect))
            x = c_int16(lParam & 0xffff).value / float(win_rect.w)
            y = c_int16(lParam >> 16).value / float(win_rect.h)
            y = abs(1.0 - y)

            if msg == WM_LBUTTONDOWN:
                self.pen_events.append(('down', x, y))
                self.pen_status = True

            if msg == WM_MOUSEMOVE and self.pen_status:
                self.pen_events.append(('move', x, y))

            if msg == WM_LBUTTONUP:
                self.pen_events.append(('up', x, y))
                self.pen_status = False

        def _pen_wndProc( self, hwnd, msg, wParam, lParam ):
            if self._is_pen_message(msg):
                self._pen_handler(msg, wParam, lParam)
                return 1
            else:
                return windll.user32.CallWindowProcW(self.old_windProc, hwnd, msg, wParam, lParam)

        def start(self):
            self.uid = 0
            self.pen = None
            self.pen_status = None
            self.pen_events = []

            self.hwnd = windll.user32.GetActiveWindow()

            # inject our own wndProc to handle messages before window manager does
            self.new_windProc = WNDPROC(self._pen_wndProc)
            self.old_windProc = windll.user32.SetWindowLongW(
                self.hwnd,
                GWL_WNDPROC,
                self.new_windProc
            )

        def update(self, dispatch_fn):
            while len(self.pen_events):

                type, x, y = self.pen_events.pop(0)

                if  type == 'down':
                    self.uid += 1
                    self.pen = WM_Pen(self.device,self.uid, [x,y])
                if  type == 'move':
                    self.pen.move([x,y])

                dispatch_fn(type, self.pen)

        def stop(self):
            self.pen = None
            windll.user32.SetWindowLongW(
                self.hwnd,
                GWL_WNDPROC,
                self.old_windProc
            )

    TouchFactory.register('wm_pen', WM_PenProvider)
