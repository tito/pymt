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
    m.add_widget(v)

    v = MTVideoBase(filename='http://media11.koreus.com/00069/200910/born-in-captivity.mp4')
    v.video.play()
    m.add_widget(v)

    runTouchApp(m)
