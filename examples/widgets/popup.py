from pymt import *

m = MTWindow()

p = MTPopup(title='Example with kinetic', label_submit='Select')
k = MTKineticList(size=(400, 300), searchable=False, deletable=False, title=None)
k.add_widget(MTKineticItem(label='test1'))
k.add_widget(MTKineticItem(label='test2'))
k.add_widget(MTKineticItem(label='blehlazkdjalzidj'))
k.add_widget(MTKineticItem(label='blehlazkdjalzidj'))
k.add_widget(MTKineticItem(label='blehlazkdjalzidj'))
k.add_widget(MTKineticItem(label='blehlazkdjalzidj'))
p.add_widget(k)
m.add_widget(p)

runTouchApp()
