from pymt import *

def print_me(*largs):
	print 'CLICKED ON', largs[0].label

mms = MTWindow()
w = MTInnerWindow(size=(600, 600))
mms.add_widget(w)

# uncomment if you want a horizontal kinetic list
#k = MTKineticList(pos=(20, 20), size=(400, 400), h_limit=2, w_limit=0, do_x=True, do_y=False)
k = MTKineticList(pos=(20, 20), size=(400, 400), w_limit=3)
w.add_widget(k)

d = range(0, 20)
for x in d:
    item = MTKineticItem(label=str(x))
    item.push_handlers(on_press=curry(print_me, item))
    k.add_widget(item)

runTouchApp()
