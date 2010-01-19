from pymt import *

w = getWindow()
m = MTLabel(label='Welcome', pos=w.center, color=(1., 0, 0, 1.), font_size=12., anchor_x='center', anchor_y='middle')
m.do(Animation(duration=5, color=(0, 1., 0, 0), font_size=88.))

runTouchApp(m)
