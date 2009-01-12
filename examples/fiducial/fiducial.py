from pymt import *

c = MTContainer()

f = MTObjectWidget(parent=c, pos=(0,0), size=(100,100))

""" make sure , that you are creating a obj widget """
c.add_widget(f, 0, 'obj')

w = MTWindow(c)
#w.set_fullscreen()
runTouchApp()
