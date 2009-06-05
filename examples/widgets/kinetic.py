from pymt import *

mms = MTWindow()

k = MTKineticList(pos=(20, 20), size=(400, 400), w_limit=3)
mms.add_widget(k)

d = range(0, 50)
for x in d:
    k.add(MTKineticItem(label=str(x)), x)

@k.event
def on_delete(item, callback):
    d.remove(callback)

runTouchApp()
