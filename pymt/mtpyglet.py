"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import osc
import pyglet
from pyglet.gl import *
import sets
import sys
from Queue import Queue


#global to this module.  all event listeners will add themselves to this
# list upon creation
tuio_event_q = Queue()
touch_event_listeners = []


def intersection(set1,set2): return filter(lambda s:s in set2,set1)
def difference(set1,set2): return filter(lambda s:s not in set2,set1)

class Tuio2DCursor():
        def __init__(self, blobID,args):
                self.blobID = blobID
                self.oxpos = self.oypos = 0.0
                if len(args) < 5:
                        self.xpos, self.ypos = args[0:2]
                if len(args) == 5:
                        self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel = args[0:5]
                else:
                        self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel, self.Width , self.Height = args[0:7]

        def move(self, args):
                self.oxpos, self.oypos = self.xpos, self.ypos
                if len(args) == 5:
                        self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel = args[0:5]
                else:
                        self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel, self.Width , self.Height = args[0:7]



class TUIOGetter():
        def __init__(self,  ip='127.0.0.1', port=3333):
                osc.init()
                osc.listen('127.0.0.1', port)
                osc.bind(self.osc_2dcur_Callback, "/tuio/2Dcur")

        def osc_2dcur_Callback(self, *incoming):
		global tuio_event_q
                message = incoming[0]
                types, args = message[1], message[2:]
                #self.cur_callback(args,types)
		tuio_event_q.put([args, types])





from threading import Lock

class TouchEventLoop(pyglet.app.EventLoop):
        def __init__(self, host='127.0.0.1', port=3333):
                pyglet.app.EventLoop.__init__(self)
                self.current_frame = self.last_frame = 0
                self.alive = []
                self.blobs = {}
                self.drawingSemaphore = Lock()
                self.parser = TUIOGetter()


        def parse2dCur(self, args, types):
                global touch_event_listeners
                if args[0] == 'alive':
                        touch_release = difference(self.alive,args[1:])
                        touch_down = difference(self.alive,args[1:])
                        touch_move = intersection(self.alive,args[1:])
                        self.alive = args[1:]
                        for blobID in touch_release:
                                for l in touch_event_listeners:
                                        l.dispatch_event('on_touch_up', self.blobs, blobID, self.blobs[blobID].xpos * l.width, l.height - l.height*self.blobs[blobID].ypos)
                                del self.blobs[blobID]

                elif args[0] == 'set':
                        blobID = args[1]
                        if blobID not in self.blobs:
                                self.blobs[blobID] = Tuio2DCursor(blobID,args[2:])
                                for l in touch_event_listeners:
                                        l.dispatch_event('on_touch_down', self.blobs, blobID, self.blobs[blobID].xpos * l.width, l.height - l.height*self.blobs[blobID].ypos)

                        else:
                                self.blobs[blobID].move(args[2:])
                                for l in touch_event_listeners:
                                        l.dispatch_event('on_touch_move', self.blobs, blobID, self.blobs[blobID].xpos * l.width, l.height - l.height*self.blobs[blobID].ypos)

                                        

        def idle(self):
		global tuio_event_q
                pyglet.clock.tick()
		while not tuio_event_q.empty():
			args, types = tuio_event_q.get()
			self.parse2dCur(args, types)
                for window in pyglet.app.windows:
                        self.drawingSemaphore.acquire()
                        window.dispatch_event('on_draw')
                        window.flip()
                        self.drawingSemaphore.release()
                return 0






#any window that inherhits this or an instance will have event handlers triggered on TUIO touch events
class TouchWindow(pyglet.window.Window):

        def __init__(self, config=None):
                pyglet.window.Window.__init__(self, config=config)
                self.register_event_type('on_touch_up')
                self.register_event_type('on_touch_move')
                self.register_event_type('on_touch_down')
                touch_event_listeners.append(self)


        def on_touch_down(self, touches, touchID, x, y):
                pass
        def on_touch_move(self, touches, touchID, x, y):
                pass
        def on_touch_up(self, touches, touchID, x, y):
                pass


        def on_mouse_press(self, x, y, button, modifiers):
                #self.on_touch_down(None, "mouse", x, y)
                self.dispatch_event('on_touch_down', None, "mouse", x, y)
        def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
                self.dispatch_event('on_touch_move', None, "mouse", x, y)
        def on_mouse_release(self, x, y, button, modifiers):
                self.dispatch_event('on_touch_up', None, "mouse", x, y)
  


#static main function that starts the app loop 

def runTouchApp():
	TouchEventLoop().run()


#a very simple test
if __name__ == '__main__':
        
    from graphx import *
    touchPositions = {}
    crosshair = pyglet.sprite.Sprite(pyglet.image.load('crosshair.png'))
    crosshair.scale = 0.6

    w = TouchWindow()
    w.set_fullscreen()
    @w.event
    def on_touch_down(touches, touchID, x,y):
        touchPositions[touchID] = [(touchID,x,y)]
    @w.event
    def on_touch_up(touches, touchID,x,y):
        del touchPositions[touchID]
    @w.event
    def on_touch_move(touches, touchID, x, y):
        touchPositions[touchID].append((x,y))
    @w.event
    def on_draw():
        w.clear()
        for p in touchPositions:
            touchID,x,y = touchPositions[p][0]
            for pos in touchPositions[p][1:]:
                x, y = pos
                crosshair.x = x
                crosshair.y = y
                crosshair.draw()

    runTouchApp()

tuio_event_q.join()



