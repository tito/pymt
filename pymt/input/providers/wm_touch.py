'''
WM_TOUCH: Support of WM_TOUCH message (Window platform)
'''

__all__ = ['WM_TOUCHProvider']


import os
from ctypes import *
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ..shape import TouchShapeRect
from ...utils import curry

if 'PYMT_DOC' not in os.environ:
    from ...base import getWindow

WM_TOUCH             = 0x0240
TOUCHEVENTF_MOVE     = 0x0001
TOUCHEVENTF_DOWN     = 0x0002
TOUCHEVENTF_UP       = 0x0004
WM_MOUSEMOVE         = 512
WM_LBUTTONDOWN       = 513
WM_LBUTTONUP         = 514
MI_WP_SIGNATURE      = 0xFF515700
SIGNATURE_MASK       = 0xFFFFFF00
PEN_EVENT_TOUCH_MASK = 0x80

class TOUCHINPUT(Structure):
    _fields_= [
                ("x",c_ulong),
                ("y",c_ulong),
                ("pSource",c_ulong),
                ("id",c_ulong),
                ("flags",c_ulong),
                ("mask",c_ulong),
                ("time",c_ulong),
                ("extraInfo",c_ulong),
                ("size_x",c_ulong),
                ("szie_y",c_ulong)
               ]

    def size(self):
        return (self.size_x, self.screen_y)

    def screen_x(self):
        return self.x/100.0

    def screen_y(self):
        return self.y/100.0

    def get_event_type(self):
        if self.flags & TOUCHEVENTF_MOVE:
            return 'move'
        if self.flags & TOUCHEVENTF_DOWN:
            return 'down'
        if self.flags & TOUCHEVENTF_UP:
            return 'up'



class WM_TOUCHProvider(TouchProvider):


    def wm_touch_handler(self, win, msg, wparam, lParam):
        touches = (TOUCHINPUT * wparam)()
        windll.user32.GetTouchInputInfo(c_int(lParam), wparam, pointer(touches), sizeof(TOUCHINPUT))
        win.wm_touch_events.extend(touches)


    def mouse_msg_handler(self, win, msg, wparam, lParam):

        info = windll.user32.GetMessageExtraInfo()
        if (info & SIGNATURE_MASK) == MI_WP_SIGNATURE:
            if info & PEN_EVENT_TOUCH_MASK:
                win.last_mouse_event_device = 'touch'
        else:
            win.last_mouse_event_device = 'mouse'

        self.old_mouse_handler(msg, wparam, lParam)


    def mouse_callback_move(self, win, type, x, y,dx,dy, mod=None, button=None):
        return self.mouse_callback(win,type, x, y, mod, button)


    def mouse_callback(self, win, type, x, y, mod=None, button=None):
        if win.last_mouse_event_device == 'touch':
            return True #keep touch form doing a touch and a mouse event


    def start(self):
        self.touches = {}
        self.uid = 0

        win = getWindow()
        win.wm_touch_events = []
        windll.user32.RegisterTouchWindow(win._hwnd, 0)
        win._event_handlers[WM_TOUCH] = curry(self.wm_touch_handler, win)


        #pen and touch events come in as mouse events also
        self.old_mouse_handler = win._event_handlers[WM_MOUSEMOVE]
        win._event_handlers[WM_MOUSEMOVE] = curry(self.mouse_msg_handler, win)
        win.push_handlers(on_mouse_press   = curry(self.mouse_callback, win,'down' ) )
        win.push_handlers(on_mouse_drag    = curry(self.mouse_callback_move, win,'move') )
        win.push_handlers(on_mouse_release = curry(self.mouse_callback, win,'up' ) )



    def update(self, dispatch_fn):
        win = getWindow()
        win_x, win_y = win.get_location()

        #dispatch touch events
        while len(win.wm_touch_events):
            t = win.wm_touch_events.pop()
            x = (t.screen_x()-win_x)/float(win.width)
            y = 1.0 - (t.screen_y()-win_y)/float(win.height)

            event_type = t.get_event_type()

            #little wierd...windows first dispataches on "move" event before the down event...so do some fixing
            #i think its because it waits to check for 'gestures'...tried turning off woth win32 API call..but no luck so far
            #so for now..make sure touch_down always comes first before move or up
            if  event_type == 'up' and not self.touches.has_key(t.id):
                event_type = 'down'
            elif event_type == 'down' and self.touches.has_key(t.id):
                event_type = 'up'


            if event_type == 'down':
                self.uid += 1
                self.touches[t.id] = WM_Touch(self.device, self.uid, [x,y,t.size()])
                dispatch_fn(event_type, self.touches[t.id] )

            if event_type == 'move' and self.touches.has_key(t.id):
                self.touches[t.id].move([x,y, t.size()])
                dispatch_fn('move', self.touches[t.id] )

            if event_type == 'up'  and self.touches.has_key(t.id):
                self.touches[t.id].move([x,y, t.size()])
                dispatch_fn(event_type, self.touches[t.id] )
                del self.touches[t.id]




    def stop(self):
        win = getWindow()
        if win:
            windll.user32.UnregisterTouchWindow(win._hwnd)






class WM_Touch(Touch):

    def depack(self, args):
        self.shape = TouchShapeRect()
        self.sx, self.sy = args[0], args[1]
        self.shape.width = args[2][0]
        self.shape.height = args[2][1]
        self.profile = ('pos','shape')

        super(WM_Touch, self).depack(args)

    def __str__(self):
        return "WMTouch, id:%d, pos:(%f,%f, device:%s )" % (self.id, self.sx, self.sy, self.device)


TouchFactory.register('WM_TOUCH', WM_TOUCHProvider)
