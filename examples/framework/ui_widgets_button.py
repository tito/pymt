'''
Button example with all events in button.
'''

from pymt import *

b = MTButton(label='Push me')
@b.event
def on_press(*largs):
	print 'on_press()', b.state, largs

@b.event
def on_release(*largs):
	print 'on_release()', b.state, largs

@b.event
def on_state_change(*largs):
    print 'on_state_change()', b.state, largs

runTouchApp(b)
