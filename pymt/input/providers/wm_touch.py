__all__ = ['WM_TOUCHProvider']


from ctypes import *
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ...mtpyglet import getWindowInstances, TouchWindow



class WM_TOUCHProvider(TouchProvider):

    def start(self):
        self.touches = {}
        self.uid = 0
        for win in getWindowInstances():
            windll.user32.RegisterTouchWindow(win._hwnd, 0)


    def update(self, dispatch_fn):
        
       
        for win in getWindowInstances():
            
            win_x, win_y = win.get_location()
            while len(win.wm_touch_events):
                t = win.wm_touch_events.pop()
                x = (t.screen_x()-win_x)/float(win.width)
                y = 1.0 - (t.screen_y()-win_y)/float(win.height)
                
                event_type = t.get_event_type()


                #little wierd...windows first dispataches on "move" event before the down event
                if event_type == 'down':
                    self.uid += 1
                    self.touches[t.id] = WM_Touch(self.uid, [x,y])
                    dispatch_fn(event_type, self.touches[t.id] )
                    
                if event_type == 'move' and self.touches.has_key(t.id):
                    self.touches[t.id].move([x,y])
                    dispatch_fn('move', self.touches[t.id] )
                    
                if event_type == 'up':
                    self.touches[t.id].move([x,y])
                    dispatch_fn(event_type, self.touches[t.id] )
                    del self.touches[t.id]
                


                
                
            """    
                dispatch_fn('move', self.touches[t.id] )

                # its a current touch
                if self.touches.has_key(t.id):
                    self.touches[t.id].move([x,y])
                    dispatch_fn('move', self.touches[t.id] )
                elif old_touches.has_key(t.id):  
                    self.touches[t.id] = old_touches[t.id]
                    self.touches[t.id].move([x,y])
                    dispatch_fn('move', self.touches[t.id] )
                # its a new touch
                else:
                    self.touches[t.id] = WM_Touch(t.id, [x,y])
                    print "DOWN!", self.touches[t.id], x,y
                    dispatch_fn('down', self.touches[t.id] )

                    
            #remove the ones that disapeared
            for id in old_touches:
                if not self.touches.has_key(id):
                    dispatch_fn('up', old_touches[id] )
            """

        
    def stop(self):
        for win in getWindowInstances():
            windll.user32.UnregisterTouchWindow(win._hwnd)




class WM_Touch(Touch):
    
    def depack(self, args):
        self.sx, self.sy = args
        super(WM_Touch, self).depack(args)



TouchFactory.register('WM_TOUCH', WM_TOUCHProvider)


