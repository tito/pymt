from pymt import *
from glob import glob
from OpenGL.GL import *
import os

if __name__ == '__main__':
    base_image = os.path.join(os.path.dirname(__file__),
                              '..', 'pictures', 'images')
    w = getWindow()
    coverflow = MTCoverFlow(size=w.size)
    for filename in glob(os.path.join(base_image, '*.jpg')):
        button = MTImageButton(filename=filename)
        button.title = os.path.basename(filename)
        coverflow.add_widget(button)

    runTouchApp(coverflow)
