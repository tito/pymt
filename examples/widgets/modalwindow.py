from pymt import *

m = MTWindow()

# a back button, you will be unable to click on him
# cause the modal window will take all events
back = MTButton(label='Try to click me', pos=(200, 200))

# create a modal window
mw = MTModalWindow()

# add a button to close modal window
mb = MTButton(label='Close Modal')
@mb.event
def on_press(*largs):
	global mw
	m.remove_widget(mw)
mw.add_widget(mb)

# add back button
m.add_widget(back)

# add modal window
m.add_widget(mw)

runTouchApp()
