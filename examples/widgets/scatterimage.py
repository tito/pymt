from pymt import *
import os

current_dir = os.path.dirname(__file__)
filename = os.path.join(current_dir, 'image.jpg')

m = MTScatterImage(filename=filename, opacity=.5)
m2 = MTScatterImage(filename=filename, pos=(100, 100))

win = getWindow()
win.add_widget(m)
win.add_widget(m2)

runTouchApp()
