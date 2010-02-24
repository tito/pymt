import os
import sys
from optparse import OptionParser

import pyglet

from pymt import *
from pymt.logger import pymt_logger

from mutagen import id3
from mutagen import oggvorbis as ogg

import sqlalchemy as sql
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

def LetThemKnowTheTruth(x):
    pymt_logger.critical("You have MP3 Files!  Those suck!  Convert them to ogg and delete them!")
    pymt_logger.info("btw, if you want to implement an mp3 handler, xelapond would be very appreciative:)")
    print x
    del x #Kill the mp3 file

#TODO: Add more music types and handlers
MUSIC_TYPES = {'ogg' : ogg.Open, 'mp3' : LetThemKnowTheTruth}
IMAGE_TYPES = ['jpg', 'png']

current_dir = os.path.dirname(__file__)

def get_file_ext(file):
    return os.path.splitext(file)[1][1:]

def get_comments(file):
    ext = get_file_ext(file)
    if ext in MUSIC_TYPES:
        return MUSIC_TYPES[ext](file)
    else:
        pymt_logger.warning('File "%s" is not recognized by FlipSide', file)
        return None

def parse_comments(file):
    ext = get_file_ext(file)
    comments = get_comments(file)
    if ext == 'ogg':
        return {
            'title' : str(comments['title'].pop()),
            'path' : file,
            'album' : str(comments['album'].pop()),
            'artist' : str(comments['artist'].pop()),
            'date' : str(comments['date'].pop()),
            'tracknumber' : int(comments['tracknumber'].pop())
            }

class PlayManager(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs['pos'] = (300, 300)
        super(PlayManager, self).__init__(**kwargs)
        self.player = pyglet.media.Player()

        self.btnplay = MTButton(label='Play!',
                             bold=True)
        self.btnplay.on_press = lambda x, y, z: self.player.play()
        self.children.append(self.btnplay)

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


class SQLSongMeta(object):
    def __init__(self, title, path, album, artist, date, tracknumber, albumart):
        self.title = title
        self.path = path
        self.album = album
        self.artist = artist
        self.date = date
        self.tracknumber = tracknumber
        self.albumart = albumart

    def __repr__(self):
        return "<Song('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.title, self.path, self.album, self.artist, self.date, self.tracknumber)


class KineticSong(MTKineticItem):
    '''This holds all the info about a song, and it is usually used within the
    KineticSong objects.  I just felt it would be nice to separate the kinetic
    code from the song metadata.  When the ORM is used this is where it all gets
    put
    '''
    def __init__(self, meta, **kwargs):
        self.meta = meta
        kwargs['label'] = self.meta.title
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

    def on_press(self, child, callback):
        self.player.play(child.meta.path)


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

def main():
    # Parse command line options
    parser = OptionParser()
    parser.add_option('-d', '--directory',
                      action='store',
                      type='string',
                      default='~/Music',
                      dest='directory',
                      help="The directory to search for Music Files")
    parser.add_option('-s', '--scan',
                      action='store_true',
                      dest='scan',
                      help='Scan for music files and load them into the library')
    #parser.add_option('-r', '--reset'

    opts, args = parser.parse_args()
    if args:
        pymt_logger.warning("FlipSide doesn't know what to do with: %s")

    if opts.scan and not os.path.exists(opts.directory):
        pymt_logger.warning("Your specified music directory %s does not exist")
        sys.exit()

    w = MTWindow()

    k = MTKinetic()
    w.add_widget(k)

    p = MTScatterPlane()
    k.add_widget(p)

    player = PlayManager()
    p.add_widget(player)

    #SQL Stuff
    if not os.path.exists('library.sql'):
        #There is no library, lets generate one
        pymt_logger.warning("You don't have a music library!  To generate one, flipside.py -d /path/to/music -s")
        sys.exit()

    engine = sql.create_engine('sqlite:///library.sql', echo=False, echo_pool=False)

    metadata = MetaData()
    songs_table = Table('songs', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('title', String),
                        Column('path', String),
                        Column('album', String),
                        Column('artist', String),
                        Column('date', String),
                        Column('tracknumber', Integer),
                        Column('albumart', String)
                        )

    metadata.create_all(engine)

    mapper(SQLSongMeta, songs_table)

    session = sessionmaker(bind=engine, echo_uow=False)()

    ## NEW METHOD##
    #Find all the music in MUSIC_DIR and put it in our SQL DB
    if opts.scan:
        music_tree = os.walk(os.path.expanduser(opts.directory))
        for branch in music_tree:
            try:
                cover = os.path.join(branch[0], filter(lambda x: get_file_ext(x) in IMAGE_TYPES, branch[2]).pop())
            except:
                cover = 'cover_default.jpg'

            for file in branch[2]:
                path = os.path.join(branch[0], file)
                comments = parse_comments(path)
                if comments:
                    comments['albumart'] = cover
                    song = SQLSongMeta(**comments)
                    session.add(song)

        session.commit()

    #Create a list of every album in the database
    #We use list(set()) so each album only appears once
    #The list comprehension is to get it out of the list tuple and out of unicode
    albums = [str(e[0]) for e in set(session.query(SQLSongMeta.album).all())]

    for album in albums:
        #Get a list of every song in the album "album" in the order that they appear on the CD
        songs = session.query(SQLSongMeta).filter(SQLSongMeta.album==album).order_by(SQLSongMeta.tracknumber)
        f = AlbumFloater(filename=songs[0].albumart, player=player, album=album, artist=songs[0].artist)
        for song in songs:
            #Add all the songs on the album to the floater
            f.list.add(KineticSong(meta=song))

        p.add_widget(f)

    runTouchApp()

if __name__ == '__main__':
    main()
