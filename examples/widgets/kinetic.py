from pymt import *

def print_me(*largs):
	print 'CLICKED ON', largs[0].label

mms = MTWindow()

#k = MTKineticList(pos=(20, 20), size=(400, 400), h_limit=2, w_limit=0, do_x=True, do_y=False)
k = MTKineticList(pos=(20, 20), size=(400, 400), w_limit=3)
mms.add_widget(k)

d = range(0, 50)
for x in d:
    item = MTKineticItem(label=str(x))
    item.push_handlers(on_press=curry(print_me, item))
    k.add_widget(item)
runTouchApp()
