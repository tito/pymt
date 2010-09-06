from pymt import *

# callback for the buttons
def test_button(btn, *largs):
    print 'button pressed', btn.label

# create a grid layout with 2 rows
layout = MTGridLayout(rows=2)
for x in xrange(22):
    btn = MTToggleButton(label='label%d' % x)
    btn.connect('on_press', curry(test_button, btn))
    layout.add_widget(btn)

# create a list of 400x200 size, and disable scrolling on Y axis
lst = MTList(size=(400, 200), do_y=False)
lst.add_widget(layout)

# center the list on the screen
anchor = MTAnchorLayout()
anchor.add_widget(lst)

runTouchApp(anchor)
