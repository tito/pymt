from pymt import *
from glob import glob
from OpenGL.GL import *
import os

if __name__ == '__main__':
    base_image = os.path.join(os.path.dirname(__file__),
                          '..', 'apps', 'pictures', 'images')
    coverflow = MTCoverFlow(size_hint=(1, 1),
            trigger_cover_distance=100)
    for filename in glob(os.path.join(base_image, '*.jpg')):
        button = MTImageButton(image=Loader.image(filename))
        button.title = os.path.basename(filename)
        coverflow.add_widget(button)

    @coverflow.event
    def on_change(cover):
        print('cover changed', cover.title)

    @coverflow.event
    def on_select(cover):
        print('cover selected', cover.title)

    runTouchApp(coverflow)
