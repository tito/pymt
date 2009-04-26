from pymt import *
sb = MTStencilContainer(size=(200, 200))
s = MTStencilContainer(size=(50, 50))
s.add_widget(MTLabel(label="XXXXXXXXXX", pos=(100, 100), font_size=16))
s.add_widget(MTLabel(label="XXXXXXXXXXXXXXXXXXXXXXXXXXXXX", pos=(150, 50), font_size=16))
s.add_widget(MTLabel(label="XXXXXXXXXXXXXXXXXXXXXXXXXXXXX", pos=(100, 150), font_size=16))
s.add_widget(MTLabel(label="XXXXXXXXXXXXXXXXXXXXXXXXXXXXX", pos=(0, 0), font_size=16))
sb.add_widget(s)
w = MTWindow()
w.add_widget(sb)
runTouchApp()

