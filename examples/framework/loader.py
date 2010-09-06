from pymt import *

# asynchronous load the image in http
img = Loader.image('http://pymt.eu/styles/logo.png')

# add a container with the core image, and display it
runTouchApp(MTContainer(img))
