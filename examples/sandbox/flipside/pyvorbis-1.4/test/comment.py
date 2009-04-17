#!/usr/bin/python

from ogg.vorbis import VorbisComment

def test():
    x = VorbisComment()
    x['hey'] = 'you'
    x['me'] = 'them'
    x['hEy'] = 'zoo'
    x['whee'] = 'them'
    x['Hey'] = 'boo'
    
    del x['hey']
    try:
        print x['hey'] # should fail
        assert(0)
    except KeyError: pass
test()
