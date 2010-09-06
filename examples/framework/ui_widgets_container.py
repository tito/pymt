from pymt import *
import os

# load an image
current_dir = os.path.dirname(__file__)
image = Image(os.path.join(current_dir, 'image.jpg'))

# create a scatter container, and put the image in
scatter = MTScatterContainer(image)

runTouchApp(scatter)
