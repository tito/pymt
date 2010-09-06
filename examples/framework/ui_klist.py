from pymt import *

# create a list with no possibility to move on Y axis
wlist = MTList(size=getWindow().size, do_y=False)

# create a grid layout to use inside the list
wlayout = MTGridLayout(rows=5)
wlist.add_widget(wlayout)

# create a lot of button. you should be able to click on it, and
# move the list in X axis
for x in xrange(100):
    wlayout.add_widget(MTToggleButton(label=str(x)))

runTouchApp(wlist)
