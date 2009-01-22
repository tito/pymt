# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Video Player'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_DESCRIPTION = 'This shows how to use the video player module present in the library'

from pymt import *
from pyglet.media import *
from pymt.ui.videowidget import *


if __name__ == '__main__':
    w = MTWindow()
    w.set_fullscreen()
    video = MTVideo('simpsons.avi',(100,200))
    w.add_widget(video)
    
    video2 = MTVideo('ninja-cat.avi',(600,200))
    w.add_widget(video2)
    
    video3 = MTVideo('super-fly.avi',(550,500))
    w.add_widget(video3)
    
    video4 = MTVideo('video.avi',(440,300))
    w.add_widget(video4)
    
    runTouchApp()
