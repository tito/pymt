from pymt import *
import os

# just get the image
current_dir = os.path.dirname(__file__)
filename = os.path.join(current_dir, 'image.jpg')

# create 2 scatter with image
m = MTScatterImage(filename=filename, opacity=.5)
m2 = MTScatterImage(filename=filename, pos=(100, 100))

win = getWindow()
win.add_widget(m)
win.add_widget(m2)

runTouchApp()
