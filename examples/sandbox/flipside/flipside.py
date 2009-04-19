import os
from pymt import *
from pymt.logger import pymt_logger
import pyglet
from mutagen import id3
from mutagen import oggvorbis as ogg

#TODO: Add more music types and handlers
MUSIC_TYPES = {'ogg' : ogg.Open}
IMAGE_TYPES = ['jpg', 'png']

def get_file_ext(file):
    return file.split('/').pop().split('.').pop().lower()
 
def get_comments(file):
    ext = get_file_ext(file)
    if ext in MUSIC_TYPES:
        return MUSIC_TYPES[ext](file)
    else:
        pymt_logger.warning('File "%s" is not recognized by FlipSide', file)
        return None

class PlayManager(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs['pos'] = (300, 300)
        super(PlayManager, self).__init__(**kwargs)
        self.player = pyglet.media.Player()

        self.play = MTButton(label='Play!', 
                             bold=True)
        self.play.on_press = lambda x, y, z: self.player.play()
        self.children.append(self.play)

    def play(self, file):
        self.player.seek(0)
        source = pyglet.media.load(file, streaming=True)
        self.player.queue(source)
        if self.player.playing:
            self.player.next()
        else:
            self.player.play()

    def queue(self, file):
        source = pyglet.media.load(file, streaming=True)
        self.player.queue(source)
        print file
        print 'foo'

class KineticSong(MTKineticItem):
    def __init__(self, **kwargs):
        self.path = kwargs.get('path')
        self.comments = kwargs.get('comments')
        self.name = self.comments['title']
        kwargs['label'] = self.name.pop()
        kwargs['size'] = (300, 40)
        super(KineticSong, self).__init__(**kwargs)

class SongList(MTKineticList):
    def __init__(self, **kwargs):
        kwargs.setdefault('pos', (45, 0))
        kwargs.setdefault('size', (310, 400))
        kwargs.setdefault('deletable', False)
        kwargs.setdefault('searchable', False)
        
        super(SongList, self).__init__(**kwargs)
        self.player = kwargs.get('player')

        self.pb = MTButton(label='Play', 
                           bgcolor=(0, 1, 0, .5), 
                           bold=True, pos=(self.x, self.y+self.height-40),
                           size=(80, 40))

        self.pb.on_press = lambda x, y, z: map(lambda s: self.player.queue(s.path), reversed(self.children))
        self.widgets.append(self.pb)

    def add_song(self, path, comments):
        print path
        self.add(KineticSong(comments=comments, path=path))
        #self.sort()

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

        self.album = kwargs.get('album')
        self.artist = kwargs.get('artist')
        
        self.list = SongList(player=kwargs.get('player'), title=self.album)
        self.add_widget(self.list, 'back')
  
        #TODO: Make this more efficient, it makes me drop from 25 FPS to 5
        '''if self.artist or self.album:
            self.album_lbl = MTLabel(text=self.album, font_size=12, pos=(5, 3))
            self.artist_lbl = MTLabel(text=self.artist, font_size=12, pos=(5, 16))
            self.rect = MTRectangularWidget(pos=(0, 0), size=(self.width, 40))
        
            self.add_widget(self.rect, 'front')
            self.add_widget(self.album_lbl, 'front')
            self.add_widget(self.artist_lbl, 'front')'''
        
    def on_touch_down(self, touches, touchID, x, y):
        if touches[touchID].is_double_tap:
            self.flip()

        #TODO: FIGURE OUT WHY IT WORKS THIS WAY AND NOT: super(AlbumFloater, self).on_touch_down(self, touches, touchID, x, y)###
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
        


#Set this to your music directory
'''FlipSide expects your directory to be formatted as follows:
Root Music Dir
---Artist 1
   ---Album 1
      ---Song 1
      ---Song 2
      ---Song ...
      ---Song n
   ---Album 2
      ---Song 1
      ---Song 2
      ---Song ...
      ---Song n
   ---Album n
      ---Song 1
      ---Song 2
      ---Song ...
      ---Song n
---Artist 2
   ---Album 1
      ---Song 1
      ---Song 2
      ---Song ...
      ---Song n
   ---Album 2
      ---Song 1
      ---Song 2
      ---Song ...
      ---Song n
   ---Album n
      ---Song 1
      ---Song 2
      ---Song ...
      ---Song n
'''
MUSIC_DIR = '/home/alex/Music'
music_tree = os.walk(MUSIC_DIR)

albums = []

player = PlayManager()

w = MTWindow()

k = MTKinetic()
w.add_widget(k)

p = MTScatterPlane()
k.add_widget(p)

p.add_widget(player)

for branch in music_tree:
    path = branch[0]
    songs = filter(lambda x: get_file_ext(x) in MUSIC_TYPES, branch[2])
    try:
        cover = filter(lambda x: get_file_ext(x) in IMAGE_TYPES, branch[2]).pop(0)
        cover = os.path.join(path, cover)
    except:
        cover = '/home/alex/Desktop/cover.jpg'
    if branch[2]:
        t = path.split('/')
        album = t.pop()
        artist = t.pop()
        a = AlbumFloater(filename=cover, player=player, album=album, artist=artist)
        for song in songs:
            file = os.path.join(path, song)
            com = get_comments(file)
            if not com:
                #The file is not supported, skip it
                continue
            a.list.add_song(file, com)
        a.list.sort()
        p.add_widget(a)



runTouchApp()
