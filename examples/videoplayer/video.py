# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Video Player'
PLUGIN_AUTHOR = 'Sharath Patali '
PLUGIN_DESCRIPTION = 'This shows how to use the video player module present in the library'

from pymt import *
from pyglet.media import *


if __name__ == '__main__':
    w = MTWindow()
    
    
    #normal MTVideo
    video = MTVideo(filename='super-fly.avi',pos=(0,0),on_playback_end='loop',volume=0.1)
    scat = MTScatterWidget(size=video.size)
    scat.add_widget(video)    
    w.add_widget(scat)
   
    #@video.event
    #def on_playback_end():
    #    print "playback ended"
    
    #Simple Video Widget
    #video2 = MTSimpleVideo(filename='super-fly.avi',volume=0.1,pos=(300,200))
    #w.add_widget(video2)

    runTouchApp()
