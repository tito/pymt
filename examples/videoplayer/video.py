# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Video Player'
PLUGIN_AUTHOR = 'Sharath Patali '
PLUGIN_DESCRIPTION = 'This shows how to use the video player module present in the library'

from pymt import *


if __name__ == '__main__':
    w = MTWindow()


    #normal MTVideo
    video = MTVideo(filename='super-fly.avi',on_playback_end='loop',volume=0.1, autostart=True)
    scat = MTScatterWidget(size=video.size, pos=(20, 20))
    connect(video, 'on_resize', scat, 'size')
    scat.add_widget(video)
    w.add_widget(scat)

    runTouchApp()
