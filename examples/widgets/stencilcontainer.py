from pymt import *
s = MTStencilContainer(size=(200, 200))
s.add_widget(MTLabel(text="plop", pos=(100, 100), font_size=16))
s.add_widget(MTLabel(text="a very very long sentence !", pos=(100, 150), font_size=16))
w = MTWindow()
w.add_widget(s)
runTouchApp()

