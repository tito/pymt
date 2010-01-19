from pymt import *
import os

current_dir = os.path.dirname(__file__)

c = MTScatterContainer(Image(os.path.join(current_dir, 'image.jpg')))

runTouchApp(c)
