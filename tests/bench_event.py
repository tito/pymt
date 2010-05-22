from time import time
from pymt import *

OverheadWidget = MTWidget

call = 0
frames = 1000

def on_call(*largs):
    global call
    call += 1

# start to build a scene graph
root = OverheadWidget()
for x in xrange(10):
    m = OverheadWidget()
    for x in xrange(100):
        m.add_widget(OverheadWidget())
    root.add_widget(m)

# time !
ds = time()
for x in xrange(frames):
    root.dispatch_event('on_update')
ds = time() - ds
fps = frames / ds
print 'Finished ! Time=%.5f, FPS=%.2f' % (ds, fps)
