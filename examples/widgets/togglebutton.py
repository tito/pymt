from pymt import *

b = MTToggleButton(label='Push me')
@b.event
def on_press(*largs):
	print 'on_press()', b.state, largs

@b.event
def on_release(*largs):
	print 'on_release()', b.state, largs

runTouchApp(b)
