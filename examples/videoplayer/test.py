from pymt import *


class MTVideoBase(MTScatterWidget):
    def __init__(self, filename, **kwargs):
        super(MTVideoBase, self).__init__(**kwargs)
        self.video = Video(filename=filename)

    def draw(self):
        self.size = self.video.size
        self.video.draw()


if __name__ == '__main__':

    m = MTWidget()

    v = MTVideoBase(filename='super-fly.avi')
    v.video.play()
    v.video.volume = 0.1
    m.add_widget(v)

    v = MTVideoBase(filename='http://samples.mplayerhq.hu/MPEG-4/MP4_with_ttxtSUB/1Video_2Audio_2SUBs(timed%20text%20streams).mp4')
    v.video.play()
    m.add_widget(v)

    runTouchApp(m)
