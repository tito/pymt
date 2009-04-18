import os
from pymt import *
from pymt.logger import pymt_logger
import pyglet
from mutagen import id3
from cStringIO import StringIO
from mutagen import oggvorbis as ogg
import glob

def get_comments(file):
    ext = file.split('/').pop().split('.').pop().lower()
    if ext == 'ogg':
        return ogg.Open(file)
    elif ext == 'mp3':
        return id3.Open(file)
    else:
        pymt_logger.warning('File "%s" is not recognized by FlipSide', file)
        return None

class PlayManager(MTScatterWidget):
    def __init__(self, **kwargs):
        super(PlayManager, self).__init__(**kwargs)
        self.player = pyglet.media.Player()

    def play(self, file):
        self.player.seek(0)
        source = pyglet.media.load(file, streaming=True)
        self.player.queue(source)
        if self.player.playing:
            self.player.next()
        else:
            self.player.play()

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
        self.player = kwargs.get('player')

    def add_song(self, path, comments):
        print path
        self.add(KineticSong(comments=comments, path=path))
        self.sort()

    def sort(self):
        self.pchildren.sort(lambda *l: (lambda x, y: y - x)(*[int(i.comments['tracknumber'].pop()) for i in l]))
        self.children = self.pchildren

    def on_press(self, child, callback):
        print child
        self.player.play(child.path)

class AlbumFloater(MTScatterImage):
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (400, 400))
        super(AlbumFloater, self).__init__(**kwargs)
        self.image.pos = (0, 0)
        self.scale = 400.0/float(self.image.width)
        self.image.scale = self.scale

        self.list = SongList(player=kwargs.get('player'))
        self.add_widget(self.list, 'back')

        self.album = kwargs.get('album')
        self.artist = kwargs.get('artist')
        
        self.album_lbl = MTLabel(text=self.album, font_size=12, pos=(5, 3))
        self.artist_lbl = MTLabel(text=self.artist, font_size=12, pos=(5, 16))
        self.rect = MTRectangularWidget(pos=(0, 0), size=(self.width, 40))

        self.add_widget(self.rect, 'front')
        self.add_widget(self.album_lbl, 'front')
        self.add_widget(self.artist_lbl, 'front')

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

##EVERYTHING PAST HERE IS TESTING
#It will be replaces(probably tomorrow) with real code.

w = MTWindow(fullscreen=False, size=(600, 600))

k = MTKinetic()
w.add_widget(k)

p = MTScatterPlane()
k.add_widget(p)

x = PlayManager()

s = AlbumFloater(filename='/home/alex/Desktop/cover.jpg', player=x, artist='Pink Floyd', album='Wish You Were Here')

s.add_widget(MTButton(), side='back')

for file in glob.glob('/home/alex/Music/Pink Floyd/Wish You Were Here/*.*'):
    print get_comments(file)
    s.list.add_song(file, get_comments(file))

p.add_widget(s)
p.add_widget(x)

runTouchApp()
