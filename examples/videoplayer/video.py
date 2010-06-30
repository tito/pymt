from pymt import *
from os.path import dirname, join

current_dir = dirname(__file__)

if __name__ == '__main__':
    filename = join(current_dir, 'softboy.avi')
    video = MTVideo(filename=filename, autostart=True)
    scat = MTScatterWidget(size=video.size, pos=(20, 20))
    connect(video, 'on_resize', scat, 'size')
    scat.add_widget(video)

    runTouchApp(scat)
