from time import time
from pymt import *

call = 0
frames = 1000

def on_call(*largs):
    global call
    call += 1

# start to build a scene graph
root = MTWidget()
for x in xrange(10):
    m = MTWidget()
    for x in xrange(100):
        m.add_widget(MTWidget())
    root.add_widget(m)

# time !
ds = time()
for x in xrange(frames):
    root.dispatch_event('on_update')
ds = time() - ds
fps = frames / ds
print 'Finished ! Time=%.5f, FPS=%.2f' % (ds, fps)
