__all__ = ['WM_TOUCHProvider']


from ctypes import *
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ...mtpyglet import getWindow, TouchWindow, getEventLoop
from ...utils import curry






class WM_TOUCHProvider(TouchProvider):

    def pen_callback_move(self, win, type, x, y,dx,dy, mod=None, button=None):
        return self.pen_callback(win,type, x, y, mod, button)
        
    def pen_callback(self, win, type, x, y, mod=None, button=None):        
        if not win.last_mouse_event_device == 'pen':
            if win.last_mouse_event_device == 'touch':
                return True #keep touch form doing a touch and a mouse event
            return False #it was something else...just ignore
  
        x = float(x)/win.width
        y = float(y)/win.height
        self.pen_events.append( (type,x,y) )
        return True



    def start(self):
        self.touches = {}
        self.pen = None
        self.pen_events = []
        self.uid = 0
        
        for win in getWindowInstances():
            windll.user32.RegisterTouchWindow(win._hwnd, 0)
            
            #pen and touch events come in as mouse events also
            win.push_handlers(on_mouse_press   = curry(self.pen_callback, win,'down' ) )
            win.push_handlers(on_mouse_drag    = curry(self.pen_callback_move, win,'move') )
            win.push_handlers(on_mouse_release = curry(self.pen_callback, win,'up' ) )



    def update(self, dispatch_fn):
        for win in getWindowInstances():
            skipped = []
            win_x, win_y = win.get_location()
            
            #dispatch pen events
            while len(self.pen_events):
                type,x,y = self.pen_events.pop(0)
                
                if  type == 'down':
                    self.uid += 1 
                    self.pen = WM_TOUCHProvider.create(self.uid, [x,y], device='pen')

            
                if  self.pen:
                    self.pen.move([x,y])
                    dispatch_fn(type, self.pen )
                    
                if type == 'up':
                    self.pen = None

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
                    skipped.append(t)

                if event_type == 'down':
                    self.uid += 1
                    self.touches[t.id] = WM_TOUCHProvider.create(self.uid, [x,y])
                    dispatch_fn(event_type, self.touches[t.id] )
                    
                if event_type == 'move' and self.touches.has_key(t.id):
                    self.touches[t.id].move([x,y])
                    dispatch_fn('move', self.touches[t.id] )
                    
                if event_type == 'up'  and self.touches.has_key(t.id):
                    self.touches[t.id].move([x,y])
                    dispatch_fn(event_type, self.touches[t.id] )
                    del self.touches[t.id]
                    
            win.wm_touch_events.extend(skipped) #remeber the ones we skipped because there wa sno "down event yet"
                        

        
    def stop(self):
        for win in getWindowInstances():
            windll.user32.UnregisterTouchWindow(win._hwnd)



    @staticmethod
    def create(id, pos, device='touch', area=0 ):
        return WM_Touch(id, pos , device )



class WM_Touch(Touch):
    
    def __init__(self, id, pos, device='touch'):
        super(WM_Touch, self).__init__(id, pos)
        self.device = device
        
    def depack(self, args):
        if len(args) == 2:
            self.sx, self.sy = args
        elif len(args) == 4:
            self.shape = TouchShapeRect()
            self.sx, self.sy = args[0], args[1]
            self.shape.width = args[2]
            self.shape.height = args[3]
            self.profile = ('pos','shape')
        else:
            raise InvalidArgumnetListException("WM_Touch needs either 2 (position only) or 4 (with shape) arguments")
            
        super(WM_Touch, self).depack(args)
        
    def __str__(self):
        return "WMTouch, id:%d, pos:(%f,%f, device:%s )" % (self.id, self.sx, self.sy, self.device)




TouchFactory.register('WM_TOUCH', WM_TOUCHProvider)


