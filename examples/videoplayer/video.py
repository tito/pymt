# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Video Player'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_DESCRIPTION = 'This shows how to use the video player module present in the library'

from pymt import *
from pyglet.media import *
from pymt.ui.videowidget import *


if __name__ == '__main__':
    w = MTWindow(fullscreen=True)

    video = MTVideo(video='softboy.avi',pos=(100,200))
    w.add_widget(video)

    video2 = MTVideo(video='ninja-cat.avi',pos=(600,200))
    w.add_widget(video2)

    video3 = MTVideo(video='super-fly.avi',pos=(550,500))
    w.add_widget(video3)

    video4 = MTVideo(video='video.avi',pos=(440,300))
    w.add_widget(video4)

    runTouchApp()
