from pymt import *

# callback for the buttons
def test_button(btn, *largs):
    print 'button pressed', btn.label

# create a grid layout with 2 rows
layout = MTGridLayout(rows=4)
for x in xrange(50):
    btn = MTToggleButton(label='label%d' % x)
    btn.connect('on_press', curry(test_button, btn))
    layout.add_widget(btn)

# create a list of 400x400 size
# default is on both axis
lst = MTList(size=(400, 400))
lst.add_widget(layout)

# center the list on the screen
anchor = MTAnchorLayout()
anchor.add_widget(lst)

runTouchApp(anchor)
