import os
from pymt import *
import pyglet
from mutagen.id3 import ID3 
from cStringIO import StringIO
from mutagen import oggvorbis as ogg
import glob

class PlayManager(MTScatterWidget):
    def __init__(self, **kwargs):
        self.player = pyglet.media.Player()
        


class KineticSong(MTKineticItem):
    def __init__(self, **kwargs):
        self.path = kwargs.get('path')
        self.comments = kwargs.get('comments')
        self.name = self.comments['title']
        kwargs['label'] = self.name.pop()
        super(KineticSong, self).__init__(**kwargs)

class SongList(MTKineticList):
    def __init__(self, **kwargs):
        kwargs.setdefault('pos', (0, 0))
        kwargs.setdefault('size', (400, 400))
        super(SongList, self).__init__(**kwargs)
        #self.player = kwargs.get('player')

    def add_song(self, path):
        comments = ogg.Open(path)
        self.add(KineticSong(comments=comments))
        self.sort()

    def sort(self):
        self.pchildren.sort(lambda *l: (lambda x, y: y - x)(*[int(i.comments['tracknumber'].pop()) for i in l]))
        self.children = self.pchildren

class AlbumFloater(MTScatterImage):
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (400, 400))
        super(AlbumFloater, self).__init__(**kwargs)
        self.image.pos = (0, 0)
        self.scale = 400.0/float(self.image.width)
        self.image.scale = self.scale

        self.list = SongList()
        self.add_widget(self.list, 'back')

    def on_touch_down(self, touches, touchID, x, y):
        if touches[touchID].is_double_tap:
            self.flip()

        ###TODO: FIGURE OUT WHY IT WORKS THIS WAY AND NOT: super(AlbumFloater, self).on_touch_down(self, touches, touchID, x, y)###
        # if the touch isnt on teh widget we do nothing
        if not self.collide_point(x,y):
            return False

        # let the child widgets handle the event if they want
        lx,ly = self.to_local(x,y)
        if super(MTScatterWidget, self).on_touch_down(touches, touchID, lx, ly):
            return True

        # if teh children didnt handle it, we bring to front & keep track of touches for rotate/scale/zoom action
        self.bring_to_front()
        self.touches[touchID] = Vector(x,y)
        return True
        
#MUSIC_DIR = '/home/alex/Music'
#music_tree = os.walk(MUSIC_DIR)

w = MTWindow(fullscreen=False, size=(600, 600))

k = MTKinetic()
w.add_widget(k)

p = MTScatterPlane()
k.add_widget(p)

s = AlbumFloater(filename='/home/alex/Desktop/cover.jpg')

s.add_widget(MTButton(), side='back')

for file in glob.glob('/home/alex/Music/Pink Floyd/Wish You Were Here/*.ogg'):
    print file
    s.list.add_song(file)

#s.sort()



p.add_widget(s)

runTouchApp()
