#!/usr/bin/env python

'''
ogg123.py

By Andrew Chatham
Based on ogg123.c by Keneth Arnold.

Used to demonstrate the ogg and ao Python bindings.  If you just want
to cut to the chase and see how to use the modules, the actual work is
in Player.start

Run "ogg123.py --help" for instructions on usage.
'''

import sys
import string
import re
import os
import whrandom
import time

import ogg.vorbis
    
version = 'ogg123.py, version 0.0.1'
verbose = 1

usage_str = '''
Usage: ogg123.py [options] files

--help                     This output
--version                  Version information
--device=<device>          Select the output device for ao module.
--device-option=<options>  Give options to the ao module (unimplemented)
--module=[ao, lad]         Select the ao or linuxaudiodev module for output
--verbose                  Give verbose output
--quiet                    Shut up
--shuffle                  Randomize the listed files before playing
'''

class Player:
    '''A simple wrapper around an Ao object which provides an interface
    to play a specified file.'''
    
    def play(self, name):
        '''Play the given file on the current device.'''
        if os.path.isfile(name):
            vf = ogg.vorbis.VorbisFile(name)
        else:
            raise ValueError, "Play takes a filename."
        
        self.start(vf)

    def start(self, vf):
        '''Actually start playing the given VorbisFile.'''
        if verbose:
            vc = vf.comment()
            vi = vf.info()

            print 'Bitstream is %s channel, %s rate' % (vi.channels, vi.rate)
            
            # If any of these comments show up, print 'key: val' where
            recognized_comments = ('Artist', 'Album', 'Title', 'Version',
                                   'Organization', 'Genre', 'Description',
                                   'Date', 'Location', 'Copyright', 'Vendor')

            comment_dict = {}
            for com in recognized_comments:
                comment_dict[string.upper(com)] = '%s: %%s' % com
            known_keys = comment_dict.keys()
            
            for key, val in vc.items():
                if key in known_keys:
                    print comment_dict[key] % val
                else:
                    print "Unknown comment: %s" % val

            print

        # Here is the little bit that actually plays the file.
        # Read takes the number of bytes to read and returns a tuple
        # containing the buffer, the number of bytes read, and I have
        # no idea what the bit thing is for! Then write the buffer contents
        # to the device.
        
        while 1:
            (buff, bytes, bit) = vf.read(4096)
            if verbose == 2:
                print "Read %s bytes" % bytes
                
            if bytes == 0:
                break
            self.write(buff, bytes)

class AOPlayer(Player):
    '''A player which uses the ao module.'''

    def __init__(self, id=None):
        import ao
        if id is None:
            id = ao.driver_id('esd')
        self.dev = ao.AudioDevice(id)

    def write(self, buff, bytes):
        self.dev.play(buff, bytes)

class LADPlayer(Player):
    '''A player which uses the linuxaudiodev module. I have little
    idea how to use this thing. At least it plays.'''

    def __init__(self):
        import linuxaudiodev
        self.lad = linuxaudiodev
        self.dev = linuxaudiodev.open('w')
        self.dev.setparameters(44100, 16, 2, linuxaudiodev.AFMT_S16_NE)

    def write(self, buff, bytes):
        '''The write function. I'm really guessing as to whether
        I'm using it correctly or not, but this seems to work, so until I
        hear otherwise I'll go with this. Please educate me!'''
        
        while self.dev.obuffree() < bytes:
            time.sleep(0.2)
        self.dev.write(buff[:bytes])

def usage(msg=None):
    if msg:
        print msg
        print
    print version
    print usage_str

def main():
    global verbose
    import getopt
    
    args = sys.argv[1:]

    opts = 'hVd:om:vqz'
    long_opts = ('help', 'version', 'device=',
                 'device-option=',  'module=', 'verbose',
                 'quiet', 'shuffle')
    try:
        optlist, args = getopt.getopt(args, opts, long_opts)
    except getopt.error, m:
        print m
        print
        usage()
        sys.exit(2)
        
    driver_id = None
    device_options = None

    modchoice = 'ao'
    choices = {'ao': AOPlayer,
               'lad': LADPlayer}
    
    for arg, val in optlist:
        if arg == '-h' or arg == '--help':
            usage()
            sys.exit(2)
            
        elif arg == '-V' or arg == '--version':
            print version
            sys.exit(0)

        elif arg == '-d' or arg == '--device':
            try:
                driver_id = ao_get_driver_id(val)
            except aoError:
                sys.stderr.write('No such device %s\n' % val)
                sys.exit(1)
                
        elif arg == '-o' or arg == '--device-option':
            raise NotImplementedError

        elif arg == '-m' or arg == '--module':
            if choices.has_key(val):
                modchoice = val
            else:
                usage("%s is not a valid module choice" % val)
                sys.exit(2)
                
        elif arg == '-v' or arg == '--verbose':
            verbose = 2

        elif arg == '-q' or arg == '--quiet':
            verbose = 0

        elif arg == '-z' or arg == '--shuffle':
            ri = whrandom.randrange
            for pos in range(len(args)):
                newpos = ri(pos, len(args))
                tmp = args[pos]
                args[pos] = args[newpos]
                args[newpos] = tmp

    if not args: #no files to play
        usage()
        sys.exit(0)

    myplayer = choices[modchoice]() # Either AOPlayer or LADPlayer
    if verbose:
        print "Module choice: %s" % modchoice

    for file in args:
        if verbose:
            print "Playing %s" % file
            print

        myplayer.play(file)
        
if __name__ == '__main__':
    main()

