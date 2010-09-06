'''
Create a event dispatcher, and use it to get all event from PyMT
Without any OpenGL window created.
'''

# prevent window creation
import os

os.environ['PYMT_SHADOW_WINDOW'] = '0'
from pymt import *

# create a class to catch all events
class TouchEventListener:
    def dispatch_event(self, event_name, *arguments):
        print 'Event dispatched', event_name, 'with', arguments

# append the class to event listeners
pymt_event_listeners.append(TouchEventListener())

# start pymt subsystem
runTouchApp(slave=True)

# now you can run your application,
# and don't forget to update PyMT subsystem
while True:
    # update pymt subsystem
    getEventLoop().idle()

    # do your own thing.
    pass

